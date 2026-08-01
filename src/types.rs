use pyo3::prelude::*;
use pyo3::types::{PyDict, PyDictMethods};

#[pyclass(eq, eq_int, skip_from_py_object)]
#[derive(Debug, Clone, PartialEq)]
pub enum ComponentType {
    Sbc, Display, Keyboard, Power, Enclosure, Cooling,
    Pcb, Wire, Connectivity, Storage, Os,
    EnvironmentalSensor, CameraModule, Sdr, LoraMesh,
    NfcRfid, Fingerprint, HapticFeedback, Imu,
    ColorPalette, AestheticMaterial, ThermalInterface,
    UconsoleExpansion, Peripheral,
    Unknown,
}

#[pymethods]
impl ComponentType {
    fn __str__(&self) -> String { format!("{:?}", self) }
}

impl ComponentType {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().replace(' ', "_").replace('-', "_").as_str() {
            "sbc" | "sbcs" => Self::Sbc,
            "display" => Self::Display,
            "keyboard" => Self::Keyboard,
            "power" | "battery" => Self::Power,
            "enclosure" | "case" => Self::Enclosure,
            "cooling" | "cool" | "fan" | "heatsink" => Self::Cooling,
            "pcb" | "board" => Self::Pcb,
            "wire" | "cable" => Self::Wire,
            "connectivity" | "wifi" | "ethernet" => Self::Connectivity,
            "storage" | "nvme" | "ssd" | "microsd" => Self::Storage,
            "os" => Self::Os,
            "sensor" | "environmental" => Self::EnvironmentalSensor,
            "camera" => Self::CameraModule,
            "sdr" | "radio" => Self::Sdr,
            "lora" | "mesh" => Self::LoraMesh,
            "nfc" | "rfid" => Self::NfcRfid,
            "fingerprint" => Self::Fingerprint,
            "haptic" | "haptics" => Self::HapticFeedback,
            "imu" | "accelerometer" => Self::Imu,
            "palette" | "color" => Self::ColorPalette,
            "material" | "aesthetic" => Self::AestheticMaterial,
            "thermal" => Self::ThermalInterface,
            "expansion" | "uconsole" => Self::UconsoleExpansion,
            "peripheral" => Self::Peripheral,
            _ => Self::Unknown,
        }
    }
}

#[pyclass(eq, eq_int, skip_from_py_object)]
#[derive(Debug, Clone, PartialEq)]
pub enum Severity { Info, Low, Medium, High, Critical }

#[pymethods]
impl Severity {
    fn __str__(&self) -> String { format!("{:?}", self) }
}

impl Severity {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "info" => Self::Info, "low" => Self::Low,
            "medium" | "mid" => Self::Medium,
            "high" => Self::High, "critical" => Self::Critical,
            _ => Self::Medium,
        }
    }
}

#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct Component {
    #[pyo3(get, set)] pub id: String,
    #[pyo3(get, set)] pub name: String,
    #[pyo3(get, set)] pub component_type: String,
    #[pyo3(get, set)] pub price: f64,
    #[pyo3(get, set)] pub price_str: String,
    #[pyo3(get, set)] pub category: String,
}

#[pymethods]
impl Component {
    #[new]
    pub fn new(id: String, name: String, component_type: String, price: f64,
               price_str: String, category: String) -> Self {
        Self { id, name, component_type, price, price_str, category }
    }

    fn __repr__(&self) -> String {
        format!("<Component {}: {} (${:.2})>", self.id, self.name, self.price)
    }

    fn to_dict(&self, py: Python) -> PyResult<Py<PyDict>> {
        let d = PyDict::new(py);
        d.set_item("id", &self.id)?;
        d.set_item("name", &self.name)?;
        d.set_item("type", &self.component_type)?;
        d.set_item("price", self.price)?;
        d.set_item("price_str", &self.price_str)?;
        d.set_item("category", &self.category)?;
        Ok(d.into())
    }
}

#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct Flaw {
    #[pyo3(get)] pub severity: String,
    #[pyo3(get)] pub issue: String,
    #[pyo3(get)] pub fix: String,
}

#[pymethods]
impl Flaw {
    #[new]
    pub fn new(severity: String, issue: String, fix: String) -> Self {
        Self { severity, issue, fix }
    }

    fn to_dict(&self, py: Python) -> PyResult<Py<PyDict>> {
        let d = PyDict::new(py);
        d.set_item("severity", &self.severity)?;
        d.set_item("issue", &self.issue)?;
        d.set_item("fix", &self.fix)?;
        Ok(d.into())
    }
}

#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct BuildAudit {
    #[pyo3(get)] pub flaws_found: u32,
    pub flaws: Vec<Flaw>,
    #[pyo3(get)] pub fixes_applied: Vec<String>,
    #[pyo3(get)] pub compatibility_score: u8,
    #[pyo3(get)] pub passed: bool,
}

impl BuildAudit {
    pub fn new(flaws_found: u32, flaws: Vec<Flaw>, fixes_applied: Vec<String>,
               compatibility_score: u8, passed: bool) -> Self {
        Self { flaws_found, flaws, fixes_applied, compatibility_score, passed }
    }

    pub fn to_dict(&self, py: Python) -> PyResult<Py<PyDict>> {
        let d = PyDict::new(py);
        d.set_item("flaws_found", self.flaws_found)?;
        let flaws_list: Vec<Py<PyDict>> = self.flaws.iter().map(|f| f.to_dict(py).unwrap()).collect();
        d.set_item("flaws", flaws_list)?;
        d.set_item("fixes_applied", self.fixes_applied.clone())?;
        d.set_item("compatibility_score", self.compatibility_score)?;
        d.set_item("passed", self.passed)?;
        Ok(d.into())
    }
}

#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct Upgrade {
    #[pyo3(get)] pub component: String,
    #[pyo3(get)] pub current: String,
    #[pyo3(get)] pub upgrade: String,
    #[pyo3(get)] pub reason: String,
    #[pyo3(get)] pub cost: f64,
    #[pyo3(get)] pub difficulty: String,
}

#[pymethods]
impl Upgrade {
    #[new]
    pub fn new(component: String, current: String, upgrade: String, reason: String,
               cost: f64, difficulty: String) -> Self {
        Self { component, current, upgrade, reason, cost, difficulty }
    }

    fn to_dict(&self, py: Python) -> PyResult<Py<PyDict>> {
        let d = PyDict::new(py);
        d.set_item("component", &self.component)?;
        d.set_item("current", &self.current)?;
        d.set_item("upgrade", &self.upgrade)?;
        d.set_item("reason", &self.reason)?;
        d.set_item("cost", self.cost)?;
        d.set_item("difficulty", &self.difficulty)?;
        Ok(d.into())
    }
}

#[pyclass(skip_from_py_object)]
#[derive(Debug, Clone)]
pub struct Model3dConfig {
    #[pyo3(get, set)] pub description: String,
    #[pyo3(get, set)] pub color: String,
    #[pyo3(get, set)] pub style: String,
    #[pyo3(get, set)] pub width: f64,
    #[pyo3(get, set)] pub height: f64,
    #[pyo3(get, set)] pub depth: f64,
}

#[pymethods]
impl Model3dConfig {
    #[new]
    pub fn new(description: String, color: String, style: String,
               width: f64, height: f64, depth: f64) -> Self {
        Self { description, color, style, width, height, depth }
    }
}

pub fn extract_str(d: &Bound<'_, PyDict>, key: &str) -> Option<String> {
    d.get_item(key).ok().and_then(|x| x.and_then(|v| v.extract::<String>().ok()))
}

pub fn extract_f64(d: &Bound<'_, PyDict>, key: &str) -> Option<f64> {
    d.get_item(key).ok().and_then(|x| x.and_then(|v| v.extract::<f64>().ok()))
}

pub fn extract_u32(d: &Bound<'_, PyDict>, key: &str) -> Option<u32> {
    d.get_item(key).ok().and_then(|x| x.and_then(|v| v.extract::<u32>().ok()))
}
