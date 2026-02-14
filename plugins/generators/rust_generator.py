"""
Rust code generator plugin.
"""

from typing import Any, Dict, List
from pydantic import Field

from plugins.base import BasePlugin, BasePluginConfig


class RustGeneratorConfig(BasePluginConfig):
    """Configuration for Rust generator."""
    rust_version: str = Field(
        default="2021",
        description="Rust edition to use"
    )


class RustGenerator(BasePlugin):
    """
    Generate Rust code for various application types.
    
    Supports Actix-web APIs, CLI tools, libraries, and more.
    """
    
    name = "rust_generator"
    version = "1.0.0"
    author = "Multi-Agent Plugins"
    description = "Generate Rust code for various application types"
    tags = ["code-generation", "rust", "programming"]
    config_class = RustGeneratorConfig
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Generate Rust code.
        
        Args:
            type: Type of code to generate (actix, cli, lib, struct, enum)
            name: Name for the application/library
            **kwargs: Additional generation options
            
        Returns:
            Dictionary with generated code
        """
        code_type = kwargs.get("type", "cli")
        
        if code_type == "actix":
            return self._generate_actix(kwargs)
        elif code_type == "cli":
            return self._generate_cli(kwargs)
        elif code_type == "lib":
            return self._generate_lib(kwargs)
        elif code_type == "struct":
            return self._generate_struct(kwargs)
        elif code_type == "enum":
            return self._generate_enum(kwargs)
        else:
            return {"error": f"Unknown code type: {code_type}"}
    
    def _generate_actix(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Actix-web API code."""
        name = kwargs.get("name", "my_api")
        endpoints = kwargs.get("endpoints", [])
        
        endpoint_code = []
        for ep in endpoints:
            path = ep.get("path", "/")
            method = ep.get("method", "GET").upper()
            
            code = f'''#[{method}("{path}")]
async fn {ep.get("handler", "handler")}() -> impl Responder {{
    HttpResponse::Ok().json(serde_json::json!({{"message": "Hello, World!"}}))
}}'''
            endpoint_code.append(code)
        
        code = f'''use actix_web::{{
    App, 
    HttpResponse, 
    HttpServer, 
    Responder
}};
use serde_json;

{chr(10).join(endpoint_code)}

#[actix_web::main]
async fn main() -> std::io::Result<()> {{
    HttpServer::new(|| {{
        App::new()
            {chr(10).join([f".service({ep.get('handler', 'handler')})" for ep in endpoints])}
    }})
    .bind("127.0.0.1:8080")?
    .run()
    .await
}}
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "actix",
            "filename": "src/main.rs"
        }
    
    def _generate_cli(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Rust CLI code."""
        name = kwargs.get("name", "my_cli")
        
        code = f'''use clap::{{Parser, Subcommand}};
use serde::{{Deserialize, Serialize}};

#[derive(Parser)]
#[command(name = "{name}")]
#[command(about = "CLI Application", long_about = None)]
struct Cli {{
    #[command(subcommand)]
    command: Commands,
}}

#[derive(Subcommand)]
enum Commands {{
    /// Run the application
    Run,
    /// Show version
    Version,
}}

fn main() {{
    let args = Cli::parse();
    
    match args.command {{
        Commands::Run => {{
            println!("Running application...");
        }}
        Commands::Version => {{
            println!("{name} v1.0.0");
        }}
    }}
}}
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "cli",
            "filename": "src/main.rs"
        }
    
    def _generate_lib(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Rust library code."""
        name = kwargs.get("name", "my_lib")
        
        code = f'''//! {name} - A Rust library

pub mod {{lib_name}};

pub use {{lib_name}}::*;
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "lib",
            "filename": "src/lib.rs"
        }
    
    def _generate_struct(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Rust struct code."""
        name = kwargs.get("name", "MyStruct")
        fields = kwargs.get("fields", [])
        
        field_code = []
        for field in fields:
            field_name = field.get("name", "field")
            field_type = field.get("type", "String")
            visibility = field.get("public", False) and "pub " or ""
            
            field_code.append(f"    {visibility}{field_name}: {field_type},")
        
        code = f'''use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct {name} {{
{chr(10).join(field_code)}
}}

impl {name} {{
    pub fn new() -> Self {{
        {name} {{
{chr(10).join([f"            {f.get('name', 'field')}: {f.get('default', 'Default::default()')}," for f in fields])}
        }}
    }}
}}

impl Default for {name} {{
    fn default() -> Self {{
        Self::new()
    }}
}}
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "struct",
            "filename": f"{name.to_lowercase()}.rs"
        }
    
    def _generate_enum(self, kwargs: Dict) -> Dict[str, Any]:
        """Generate Rust enum code."""
        name = kwargs.get("name", "MyEnum")
        variants = kwargs.get("variants", ["Variant1", "Variant2"])
        
        variant_code = []
        for variant in variants:
            if isinstance(variant, str):
                variant_code.append(f"    {variant},")
            else:
                variant_name = variant.get("name", "Variant")
                data = variant.get("data", "")
                variant_code.append(f"    {variant_name}({data}),")
        
        code = f'''use serde::{{Deserialize, Serialize}};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum {name} {{
{chr(10).join(variant_code)}
}}
'''
        
        return {
            "code": code,
            "language": "rust",
            "type": "enum",
            "filename": f"{name.to_lowercase()}.rs"
        }
