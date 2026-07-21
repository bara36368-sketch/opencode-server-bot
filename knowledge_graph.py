import json, os, time, asyncio, html
import networkx as nx
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KG_FILE = os.path.join(BASE_DIR, "knowledge_graph.json")
KG_INDEX_FILE = os.path.join(BASE_DIR, "kg_index.json")
VAULT_FILE = os.path.join(BASE_DIR, "vault.json")

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.dirty = False
        self._load()

    def _load(self):
        if os.path.exists(KG_FILE):
            try:
                with open(KG_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                for node in data.get("nodes", []):
                    self.graph.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
                for edge in data.get("edges", []):
                    self.graph.add_edge(edge["source"], edge["target"], key=edge.get("key", str(time.time())), **{k: v for k, v in edge.items() if k not in ("source", "target", "key")})
            except Exception:
                pass

    def _save(self):
        data = {
            "nodes": [{"id": n, **dict(self.graph.nodes[n])} for n in self.graph.nodes],
            "edges": [{"source": u, "target": v, **dict(d)} for u, v, d in self.graph.edges(data=True)]
        }
        with open(KG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.dirty = False

    def ensure_saved(self):
        if self.dirty:
            self._save()

    def add_entity(self, name, etype="concept", source="manual", **attrs):
        name = name.strip()
        if not name:
            return False
        if not self.graph.has_node(name):
            self.graph.add_node(name, type=etype, source=source, created=time.time(), **attrs)
            self.dirty = True
            return True
        return False

    def add_relation(self, source, relation, target, **attrs):
        source = source.strip()
        target = target.strip()
        if not source or not target:
            return False
        if not self.graph.has_node(source):
            self.graph.add_node(source, type="concept", source="auto")
        if not self.graph.has_node(target):
            self.graph.add_node(target, type="concept", source="auto")
        key = f"{relation}|{time.time()}"
        self.graph.add_edge(source, target, key=key, relation=relation, created=time.time(), **attrs)
        self.dirty = True
        return True

    async def extract_from_text(self, text, call_provider=None):
        if not call_provider:
            return 0, 0
        prompt = (
            "Extract entities and relationships from the text below. "
            "Respond with ONLY valid JSON with keys: entities (array of {name, type}), "
            "relationships (array of {source, relation, target}). "
            "Types: person, place, concept, technology, organization, event, product, other. "
            f"Text:\n{text[:3000]}"
        )
        try:
            raw = await call_provider([{"role": "user", "content": prompt}], None)
        except Exception:
            return 0, 0
        try:
            import re as _re
            m = _re.search(r"\{[\s\S]*\}", raw)
            if not m:
                return 0, 0
            data = json.loads(m.group())
        except Exception:
            return 0, 0
        ec, rc = 0, 0
        for ent in data.get("entities", []):
            if self.add_entity(ent["name"], ent.get("type", "concept"), source="extract"):
                ec += 1
        for rel in data.get("relationships", []):
            if self.add_relation(rel["source"], rel["relation"], rel["target"]):
                rc += 1
        if ec or rc:
            self._save()
        return ec, rc

    def search_entities(self, query, limit=10):
        query = query.lower()
        results = []
        for n, attrs in self.graph.nodes(data=True):
            if query in n.lower() or any(query in str(v).lower() for v in attrs.values()):
                results.append({"name": n, **attrs})
        return sorted(results, key=lambda x: x.get("created", 0), reverse=True)[:limit]

    def get_related(self, name, depth=1, max_nodes=20):
        if not self.graph.has_node(name):
            return None
        sub = nx.ego_graph(self.graph, name, radius=depth, undirected=True)
        nodes = []
        for n in sub.nodes:
            attrs = dict(self.graph.nodes[n])
            attrs["name"] = n
            nodes.append(attrs)
        edges = []
        for u, v, d in sub.edges(data=True):
            edges.append({"source": u, "target": v, "relation": d.get("relation", "related_to")})
        return {"center": name, "nodes": nodes[:max_nodes], "edges": edges[:max_nodes * 3]}

    def query(self, q):
        results = {"entities": [], "paths": [], "subgraph": None}
        ql = q.lower()
        direct = self.search_entities(q, limit=5)
        results["entities"] = direct
        for n in self.graph.nodes:
            if ql in n.lower():
                rel = self.get_related(n, depth=1)
                if rel:
                    results["subgraph"] = rel
                    break
        try:
            pairs = [(n1, n2) for n1 in self.graph.nodes for n2 in self.graph.nodes if n1 != n2]
            for n1, n2 in pairs[:50]:
                if ql in n1.lower() or ql in n2.lower():
                    for path in nx.all_simple_paths(self.graph, n1, n2, cutoff=3):
                        relations = []
                        for i in range(len(path) - 1):
                            edata = self.graph.get_edge_data(path[i], path[j])
                            if edata:
                                for k, v in edata.items():
                                    relations.append({"from": path[i], "to": path[j], "relation": v.get("relation", "?")})
                        results["paths"].append({"path": path, "relations": relations})
                        if len(results["paths"]) >= 3:
                            break
                if len(results["paths"]) >= 3:
                    break
        except Exception:
            pass
        return results

    def stats(self):
        return {"entities": self.graph.number_of_nodes(), "relationships": self.graph.number_of_edges(), "types": self._type_counts()}

    def _type_counts(self):
        counts = defaultdict(int)
        for _, attrs in self.graph.nodes(data=True):
            counts[attrs.get("type", "unknown")] += 1
        return dict(counts)

    def to_json(self):
        nodes = [{"id": n, **{k: v for k, v in attrs.items() if isinstance(v, (str, int, float, bool))}} for n, attrs in self.graph.nodes(data=True)]
        edges = [{"source": u, "target": v, **{k: v for k, v in d.items() if isinstance(v, (str, int, float, bool))}} for u, v, d in self.graph.edges(data=True)]
        return {"nodes": nodes, "edges": edges}

    def remove_entity(self, name):
        if self.graph.has_node(name):
            self.graph.remove_node(name)
            self.dirty = True
            self._save()
            return True
        return False

    def clear(self):
        self.graph.clear()
        self.dirty = True
        self._save()

_kg = None

def get_kg():
    global _kg
    if _kg is None:
        _kg = KnowledgeGraph()
    return _kg


class KnowledgeVault:
    def __init__(self):
        self.entries = {}
        self._load()

    def _load(self):
        if os.path.exists(VAULT_FILE):
            try:
                with open(VAULT_FILE, encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception:
                self.entries = {}

    def _save(self):
        with open(VAULT_FILE, "w", encoding="utf-8") as f:
            json.dump(self.entries, f, indent=2, ensure_ascii=False)

    def save(self, title, content, tags=None, uid="global"):
        eid = str(int(time.time()))
        self.entries[eid] = {"id": eid, "title": title, "content": content, "tags": tags or [], "uid": uid, "created": time.time()}
        self._save()
        return eid

    def search(self, query, uid="global"):
        q = query.lower()
        results = []
        for e in self.entries.values():
            if uid != "global" and e.get("uid") != uid:
                continue
            if q in e["title"].lower() or q in e["content"].lower() or any(q in t.lower() for t in e.get("tags", [])):
                results.append(e)
        return sorted(results, key=lambda x: x.get("created", 0), reverse=True)[:20]

    def list(self, uid="global"):
        entries = [e for e in self.entries.values() if uid == "global" or e.get("uid") == uid]
        return sorted(entries, key=lambda x: x.get("created", 0), reverse=True)

    def delete(self, eid):
        if eid in self.entries:
            del self.entries[eid]
            self._save()
            return True
        return False

    def get(self, eid):
        return self.entries.get(eid)

_vault = None

def get_vault():
    global _vault
    if _vault is None:
        _vault = KnowledgeVault()
    return _vault
