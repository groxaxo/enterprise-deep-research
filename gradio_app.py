#!/usr/bin/env python3
"""
Enterprise Deep Research - Gradio 6 Interface

A modern, user-friendly interface for conducting deep research using AI agents.
This interface provides access to all core EDR features including:
- Deep research with multi-agent orchestration
- File upload and analysis
- Database querying (Text2SQL)
- Real-time steering and guidance
- Visualization generation
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional, List, Tuple
import json
from datetime import datetime

# Add the project directory to the Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Gradio
import gradio as gr

# Import research services
from services.research import ResearchService
from models.research import ResearchRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global configuration
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "openai")
LLM_MODEL = os.environ.get("LLM_MODEL", "o3-mini")
MAX_LOOPS = int(os.environ.get("MAX_WEB_RESEARCH_LOOPS", "10"))

# Available providers and models
PROVIDERS = {
    "openai": ["o4-mini", "o4-mini-high", "o3-mini", "o3-mini-reasoning", "gpt-4o"],
    "anthropic": ["claude-sonnet-4", "claude-sonnet-4-thinking", "claude-3-7-sonnet", "claude-3-7-sonnet-thinking"],
    "google": ["gemini-2.5-pro", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"],
    "groq": ["deepseek-r1-distill-llama-70b", "llama-3.3-70b-versatile", "llama3-70b-8192"],
    "sambanova": ["DeepSeek-V3-0324"],
}


def get_models_for_provider(provider: str) -> List[str]:
    """Get available models for a given provider."""
    return PROVIDERS.get(provider, ["default"])


async def conduct_research(
    query: str,
    provider: str,
    model: str,
    max_loops: int,
    extra_effort: bool,
    minimum_effort: bool,
    enable_steering: bool,
    uploaded_files: Optional[List] = None,
    progress=gr.Progress()
) -> Tuple[str, str, str]:
    """
    Conduct deep research on the given query.
    
    Args:
        query: Research query/topic
        provider: LLM provider to use
        model: Specific model to use
        max_loops: Maximum number of research loops
        extra_effort: Enable extra effort mode
        minimum_effort: Enable minimum effort mode (1 loop)
        enable_steering: Enable real-time steering
        uploaded_files: List of uploaded file paths
        progress: Gradio progress tracker
        
    Returns:
        Tuple of (report, sources, status_message)
    """
    if not query or not query.strip():
        return "", "", "❌ Please enter a research query"
    
    try:
        progress(0.1, desc="Initializing research...")
        logger.info(f"Starting research: {query[:50]}...")
        
        # Process uploaded files if any
        uploaded_data_content = None
        if uploaded_files:
            progress(0.2, desc="Processing uploaded files...")
            file_contents = []
            for file_path in uploaded_files:
                try:
                    with open(file_path.name, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_contents.append(f"=== File: {os.path.basename(file_path.name)} ===\n{content}\n")
                except Exception as e:
                    logger.warning(f"Could not read file {file_path.name}: {e}")
            
            if file_contents:
                uploaded_data_content = "\n\n".join(file_contents)
        
        # Set environment variables for this research session
        os.environ["LLM_PROVIDER"] = provider
        os.environ["LLM_MODEL"] = model
        os.environ["MAX_WEB_RESEARCH_LOOPS"] = str(max_loops)
        
        progress(0.3, desc="Starting deep research...")
        
        # Create research request
        research_request = ResearchRequest(
            query=query,
            extra_effort=extra_effort,
            minimum_effort=minimum_effort,
            streaming=False,
            provider=provider,
            model=model,
            uploaded_data_content=uploaded_data_content,
            steering_enabled=enable_steering
        )
        
        # Conduct research
        result = await ResearchService.conduct_research(
            query=query,
            extra_effort=extra_effort,
            minimum_effort=minimum_effort,
            provider=provider,
            model=model,
            streaming=False,
            uploaded_data_content=uploaded_data_content,
            steering_enabled=enable_steering
        )
        
        progress(1.0, desc="Research complete!")
        
        # Extract results
        report = result.get("running_summary", "No report generated")
        sources = result.get("sources_gathered", [])
        sources_text = "\n".join([f"- {source}" for source in sources]) if sources else "No sources gathered"
        
        loop_count = result.get("research_loop_count", 0)
        status = f"✅ Research complete! Conducted {loop_count} research loops."
        
        return report, sources_text, status
        
    except Exception as e:
        logger.error(f"Research error: {e}", exc_info=True)
        return "", "", f"❌ Error during research: {str(e)}"


def format_research_output(report: str, sources: str, status: str) -> str:
    """Format research output into a readable markdown document."""
    output = f"""# Research Report

{report}

---

## Sources
{sources}

---

**Status**: {status}
"""
    return output


def create_gradio_interface():
    """Create the main Gradio interface."""
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .header-text {
        text-align: center;
        padding: 20px;
    }
    .output-box {
        min-height: 400px;
    }
    """
    
    with gr.Blocks(
        title="Enterprise Deep Research",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
        css=custom_css
    ) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🔍 Enterprise Deep Research
            
            **Multi-Agent AI Research System with Specialized Search, Analysis & Visualization**
            
            Conduct comprehensive research using advanced AI agents with web search, file analysis, 
            and database querying capabilities. Features adaptive planning, real-time steering, 
            and automated report generation.
            """,
            elem_classes=["header-text"]
        )
        
        with gr.Tabs() as tabs:
            
            # ============= MAIN RESEARCH TAB =============
            with gr.Tab("🔬 Deep Research"):
                gr.Markdown(
                    """
                    ### Conduct Deep Research
                    Enter your research query below. The system will:
                    1. Break down your query using the Master Planning Agent
                    2. Search using specialized agents (General, Academic, GitHub, LinkedIn)
                    3. Analyze and synthesize findings
                    4. Generate a comprehensive report with citations
                    """
                )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        # Input section
                        gr.Markdown("#### 📝 Research Query")
                        query_input = gr.Textbox(
                            label="What would you like to research?",
                            placeholder="e.g., Latest developments in quantum computing...",
                            lines=3,
                            max_lines=10
                        )
                        
                        # File upload
                        gr.Markdown("#### 📎 Upload Files (Optional)")
                        file_upload = gr.Files(
                            label="Upload documents to include in research",
                            file_types=[".txt", ".pdf", ".docx", ".csv", ".json"],
                            file_count="multiple"
                        )
                        
                        # Configuration
                        gr.Markdown("#### ⚙️ Configuration")
                        
                        with gr.Row():
                            provider_dropdown = gr.Dropdown(
                                choices=list(PROVIDERS.keys()),
                                value=LLM_PROVIDER,
                                label="LLM Provider",
                                interactive=True
                            )
                            model_dropdown = gr.Dropdown(
                                choices=get_models_for_provider(LLM_PROVIDER),
                                value=LLM_MODEL,
                                label="Model",
                                interactive=True
                            )
                        
                        max_loops_slider = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=MAX_LOOPS,
                            step=1,
                            label="Max Research Loops",
                            info="Number of research iterations (more = deeper research)"
                        )
                        
                        with gr.Row():
                            extra_effort_check = gr.Checkbox(
                                label="Extra Effort Mode",
                                value=False,
                                info="Perform more extensive research"
                            )
                            minimum_effort_check = gr.Checkbox(
                                label="Quick Mode",
                                value=False,
                                info="Force minimum effort (1 loop)"
                            )
                        
                        steering_check = gr.Checkbox(
                            label="Enable Steering",
                            value=False,
                            info="Allow real-time guidance during research"
                        )
                        
                        # Action buttons
                        with gr.Row():
                            research_btn = gr.Button(
                                "🚀 Start Research",
                                variant="primary",
                                size="lg"
                            )
                            clear_btn = gr.Button("🗑️ Clear", size="lg")
                    
                    with gr.Column(scale=1):
                        # Output section
                        gr.Markdown("#### 📊 Results")
                        
                        status_output = gr.Textbox(
                            label="Status",
                            value="Ready to start research",
                            interactive=False,
                            lines=2
                        )
                        
                        report_output = gr.Markdown(
                            label="Research Report",
                            value="*Research report will appear here...*",
                            elem_classes=["output-box"]
                        )
                        
                        sources_output = gr.Textbox(
                            label="Sources",
                            value="",
                            interactive=False,
                            lines=10,
                            max_lines=20
                        )
                        
                        # Download button
                        download_btn = gr.DownloadButton(
                            label="📥 Download Report",
                            visible=False
                        )
                
                # Event handlers
                def update_models(provider):
                    """Update model dropdown when provider changes."""
                    models = get_models_for_provider(provider)
                    return gr.Dropdown(choices=models, value=models[0])
                
                provider_dropdown.change(
                    fn=update_models,
                    inputs=[provider_dropdown],
                    outputs=[model_dropdown]
                )
                
                def run_research_wrapper(*args):
                    """Wrapper to run async research function."""
                    return asyncio.run(conduct_research(*args))
                
                research_btn.click(
                    fn=run_research_wrapper,
                    inputs=[
                        query_input,
                        provider_dropdown,
                        model_dropdown,
                        max_loops_slider,
                        extra_effort_check,
                        minimum_effort_check,
                        steering_check,
                        file_upload
                    ],
                    outputs=[report_output, sources_output, status_output]
                )
                
                def clear_all():
                    """Clear all inputs and outputs."""
                    return (
                        "",  # query
                        None,  # files
                        "",  # report
                        "",  # sources
                        "Ready to start research"  # status
                    )
                
                clear_btn.click(
                    fn=clear_all,
                    inputs=[],
                    outputs=[query_input, file_upload, report_output, sources_output, status_output]
                )
            
            # ============= INFORMATION TAB =============
            with gr.Tab("ℹ️ About"):
                gr.Markdown(
                    """
                    # About Enterprise Deep Research
                    
                    ## 🎯 Overview
                    
                    Enterprise Deep Research (EDR) is a sophisticated multi-agent system designed for 
                    comprehensive, enterprise-grade research and analysis. It combines:
                    
                    - **Master Planning Agent**: Adaptive query decomposition and research strategy
                    - **Specialized Search Agents**: 
                        - General Web Search
                        - Academic Research (scholarly articles, papers)
                        - GitHub (code, repositories, issues)
                        - LinkedIn (professional profiles, company info)
                    - **File Analysis**: Upload and analyze documents as part of research
                    - **Database Querying**: Natural language to SQL for data analysis
                    - **Visualization Agent**: Generate charts and graphs from data
                    - **Reflection Mechanism**: Detect knowledge gaps and refine research direction
                    - **Real-time Steering**: Guide research with human-in-the-loop feedback
                    
                    ## 🚀 Key Features
                    
                    ### Multi-Agent Architecture
                    - Coordinated agents working in parallel for efficient research
                    - Each agent specialized for specific types of information
                    - Automatic source validation and citation management
                    
                    ### Adaptive Research
                    - Dynamic query decomposition based on topic complexity
                    - Knowledge gap detection and automatic refinement
                    - Configurable research depth (1-20 loops)
                    
                    ### Enterprise Integration
                    - MCP (Model Context Protocol) based tool ecosystem
                    - Support for multiple LLM providers (OpenAI, Anthropic, Google, Groq, SambaNova)
                    - Local deployment support (Ollama, vLLM)
                    - Database integration for text-to-SQL capabilities
                    
                    ### Real-time Capabilities
                    - Streaming research progress
                    - Live steering commands during research
                    - Activity generation for transparency
                    
                    ## 📚 Documentation
                    
                    - **Paper**: [arXiv:2510.17797](https://arxiv.org/abs/2510.17797)
                    - **Dataset**: [EDR-200 on Hugging Face](https://huggingface.co/datasets/Salesforce/EDR-200)
                    - **GitHub**: [SalesforceAIResearch/enterprise-deep-research](https://github.com/SalesforceAIResearch/enterprise-deep-research)
                    - **Documentation**: [DeepWiki](https://deepwiki.com/SalesforceAIResearch/enterprise-deep-research)
                    
                    ## ⚙️ Configuration
                    
                    ### LLM Providers
                    
                    EDR supports multiple LLM providers:
                    
                    | Provider | Default Model | API Key Required |
                    |----------|---------------|------------------|
                    | OpenAI | o3-mini | OPENAI_API_KEY |
                    | Anthropic | claude-sonnet-4 | ANTHROPIC_API_KEY |
                    | Google | gemini-2.5-pro | GOOGLE_CLOUD_PROJECT |
                    | Groq | deepseek-r1-distill-llama-70b | GROQ_API_KEY |
                    | SambaNova | DeepSeek-V3-0324 | SAMBNOVA_API_KEY |
                    | Local (Ollama/vLLM) | User-defined | OPENAI_BASE_URL |
                    
                    ### Environment Variables
                    
                    Key configuration options:
                    
                    ```bash
                    # LLM Configuration
                    LLM_PROVIDER=openai
                    LLM_MODEL=o3-mini
                    
                    # Search Configuration
                    TAVILY_API_KEY=your-key-here
                    
                    # Research Settings
                    MAX_WEB_RESEARCH_LOOPS=10
                    
                    # Privacy Settings (disable telemetry)
                    LANGCHAIN_TRACING_V2=false
                    OTEL_SDK_DISABLED=true
                    ```
                    
                    ## 🔒 Privacy & Security
                    
                    - All telemetry can be disabled
                    - Supports fully local deployment with Ollama/vLLM
                    - No external API calls when using local models and SearXNG
                    - Data privacy controls for sensitive research
                    
                    ## 📊 Benchmarking
                    
                    EDR has been validated on multiple benchmarks:
                    
                    - **DeepResearchBench**: Comprehensive research evaluation
                    - **ResearchQA**: Question-answering with citation verification
                    - **DeepConsult**: Consulting-style analysis tasks
                    
                    The EDR-200 dataset contains 201 complete agentic research trajectories 
                    showing the full reasoning process across search, reflection, and synthesis.
                    
                    ## 🤝 Contributing
                    
                    We welcome contributions! See [CONTRIBUTING.md](https://github.com/SalesforceAIResearch/enterprise-deep-research/blob/main/CONTRIBUTING.md)
                    
                    ## 📜 License
                    
                    Licensed under [Apache 2.0](https://opensource.org/licenses/Apache-2.0)
                    
                    ## 🙏 Acknowledgments
                    
                    Built with:
                    - [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration
                    - [Tavily](https://tavily.com) - Web search
                    - [Gradio](https://gradio.app) - User interface
                    - [FastAPI](https://fastapi.tiangolo.com/) - Backend API
                    
                    ---
                    
                    **Citation**:
                    
                    ```bibtex
                    @article{prabhakar2025enterprisedeepresearch,
                      title={Enterprise Deep Research: Steerable Multi-Agent Deep Research for Enterprise Analytics},
                      author={Prabhakar, Akshara and Ram, Roshan and Chen, Zixiang and Savarese, Silvio and Wang, Frank and Xiong, Caiming and Wang, Huan and Yao, Weiran},
                      journal={arXiv preprint arXiv:2510.17797},
                      year={2025}
                    }
                    ```
                    """
                )
            
            # ============= SETTINGS TAB =============
            with gr.Tab("⚙️ Settings"):
                gr.Markdown(
                    """
                    ## Configuration Settings
                    
                    Current environment configuration:
                    """
                )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown(f"""
                        **LLM Configuration:**
                        - Provider: `{LLM_PROVIDER}`
                        - Model: `{LLM_MODEL}`
                        - Max Loops: `{MAX_LOOPS}`
                        
                        **API Keys Configured:**
                        - OpenAI: {"✅" if os.environ.get("OPENAI_API_KEY") else "❌"}
                        - Anthropic: {"✅" if os.environ.get("ANTHROPIC_API_KEY") else "❌"}
                        - Google: {"✅" if os.environ.get("GOOGLE_CLOUD_PROJECT") else "❌"}
                        - Groq: {"✅" if os.environ.get("GROQ_API_KEY") else "❌"}
                        - Tavily: {"✅" if os.environ.get("TAVILY_API_KEY") else "❌"}
                        """)
                    
                    with gr.Column():
                        gr.Markdown("""
                        **Privacy Settings:**
                        - Telemetry: Disabled
                        - Local Mode: Supported
                        
                        **To modify settings:**
                        1. Edit the `.env` file in the project root
                        2. Restart the Gradio application
                        
                        **For local deployment:**
                        See the [Local Setup Guide](https://github.com/SalesforceAIResearch/enterprise-deep-research/blob/main/LOCAL_SETUP.md)
                        """)
        
        # Footer
        gr.Markdown(
            """
            ---
            
            <div style="text-align: center; color: #666; padding: 20px;">
                <p><strong>Enterprise Deep Research</strong> v0.6.5</p>
                <p>
                    <a href="https://github.com/SalesforceAIResearch/enterprise-deep-research" target="_blank">GitHub</a> • 
                    <a href="https://arxiv.org/abs/2510.17797" target="_blank">Paper</a> • 
                    <a href="https://huggingface.co/datasets/Salesforce/EDR-200" target="_blank">Dataset</a> • 
                    <a href="https://deepwiki.com/SalesforceAIResearch/enterprise-deep-research" target="_blank">Documentation</a>
                </p>
                <p>Built with ❤️ using Gradio 6</p>
            </div>
            """
        )
    
    return demo


def main():
    """Main entry point for the Gradio application."""
    print("=" * 80)
    print("🔍 Enterprise Deep Research - Gradio Interface")
    print("=" * 80)
    print(f"Provider: {LLM_PROVIDER}")
    print(f"Model: {LLM_MODEL}")
    print(f"Max Loops: {MAX_LOOPS}")
    print("=" * 80)
    
    # Check for required API keys
    if not os.environ.get("TAVILY_API_KEY"):
        print("⚠️  Warning: TAVILY_API_KEY not set. Web search will not work.")
    
    provider_key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GOOGLE_CLOUD_PROJECT",
        "groq": "GROQ_API_KEY",
        "sambanova": "SAMBNOVA_API_KEY",
    }
    
    if LLM_PROVIDER in provider_key_map:
        key_name = provider_key_map[LLM_PROVIDER]
        if not os.environ.get(key_name):
            print(f"⚠️  Warning: {key_name} not set. LLM provider '{LLM_PROVIDER}' may not work.")
    
    print("\n🚀 Starting Gradio interface...")
    print("📝 Configure your .env file with API keys for full functionality")
    print("=" * 80)
    
    # Create and launch the interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()
