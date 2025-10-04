"""
Output formatting utilities for Memory Bank CLI
"""

import json
import sys
from typing import Any, Optional
from enum import Enum


class OutputLevel(Enum):
    """Output verbosity levels"""

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class OutputFormatter:
    """Formats and outputs CLI messages"""

    def __init__(self, output_format: str = "text", verbosity: int = 1):
        self.output_format = output_format
        self.verbosity = verbosity
        self.colors_enabled = self._colors_supported()

    def _colors_supported(self) -> bool:
        """Check if terminal supports colors"""
        try:
            return sys.stdout.isatty()
        except:
            return False

    def _format_message(self, message: str, level: str = "info") -> str:
        """Format message with appropriate styling"""
        if self.output_format == "json":
            return self._format_json_message(message, level)
        else:
            return self._format_text_message(message, level)

    def _format_text_message(self, message: str, level: str) -> str:
        """Format message for text output"""
        if not self.colors_enabled:
            return message

        colors = {
            "info": "\033[94m",  # Blue
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",  # Red
            "debug": "\033[90m",  # Gray
            "reset": "\033[0m",  # Reset
        }

        color = colors.get(level, colors["info"])
        reset = colors["reset"]

        return f"{color}{message}{reset}"

    def _format_json_message(self, message: str, level: str) -> str:
        """Format message for JSON output"""
        return json.dumps(
            {"level": level, "message": message, "timestamp": self._get_timestamp()}
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().isoformat()

    def output(self, message: str) -> None:
        """Output message to stdout"""
        print(message)

    def info(self, message: str) -> None:
        """Output info message"""
        if self.verbosity >= OutputLevel.NORMAL.value:
            formatted = self._format_message(message, "info")
            self.output(formatted)

    def success(self, message: str) -> None:
        """Output success message"""
        if self.verbosity >= OutputLevel.NORMAL.value:
            formatted = self._format_message(message, "success")
            self.output(formatted)

    def warning(self, message: str) -> None:
        """Output warning message"""
        if self.verbosity >= OutputLevel.NORMAL.value:
            formatted = self._format_message(message, "warning")
            self.output(formatted)

    def error(self, message: str) -> None:
        """Output error message"""
        if self.verbosity >= OutputLevel.NORMAL.value:
            formatted = self._format_message(message, "error")
            self.output(formatted)

    def debug(self, message: str, exc_info: bool = False) -> None:
        """Output debug message"""
        if self.verbosity >= OutputLevel.DEBUG.value:
            formatted = self._format_message(message, "debug")
            self.output(formatted)
            if exc_info:
                import traceback

                self.output(traceback.format_exc())

    def verbose(self, message: str) -> None:
        """Output verbose message"""
        if self.verbosity >= OutputLevel.VERBOSE.value:
            formatted = self._format_message(message, "info")
            self.output(formatted)

    def table(self, headers: list, rows: list) -> None:
        """Output data in table format"""
        if self.output_format == "json":
            self._output_json_table(headers, rows)
        else:
            self._output_text_table(headers, rows)

    def _output_text_table(self, headers: list, rows: list) -> None:
        """Output table in text format"""
        if not rows:
            return

        # Calculate column widths
        col_widths = [len(str(header)) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Create separator line
        separator = "+" + "+".join("-" * (width + 2) for width in col_widths) + "+"

        # Output table
        self.output(separator)

        # Headers
        header_row = (
            "|"
            + "|".join(
                f" {str(header):<{width}} "
                for header, width in zip(headers, col_widths)
            )
            + "|"
        )
        self.output(header_row)
        self.output(separator)

        # Data rows
        for row in rows:
            data_row = (
                "|"
                + "|".join(
                    f" {str(cell):<{width}} " for cell, width in zip(row, col_widths)
                )
                + "|"
            )
            self.output(data_row)

        self.output(separator)

    def _output_json_table(self, headers: list, rows: list) -> None:
        """Output table in JSON format"""
        table_data = {
            "headers": headers,
            "rows": rows,
            "timestamp": self._get_timestamp(),
        }
        self.output(json.dumps(table_data, indent=2))

    def json(self, data: Any) -> None:
        """Output data in JSON format"""
        if self.output_format == "json":
            self.output(json.dumps(data, indent=2, default=str))
        else:
            # Convert to text representation
            self.output(json.dumps(data, indent=2, default=str))

    def yaml(self, data: Any) -> None:
        """Output data in YAML format"""
        try:
            import yaml

            if self.output_format == "yaml":
                self.output(
                    yaml.dump(data, default_flow_style=False, allow_unicode=True)
                )
            else:
                self.output(
                    yaml.dump(data, default_flow_style=False, allow_unicode=True)
                )
        except ImportError:
            self.warning("YAML output requires PyYAML package. Falling back to JSON.")
            self.json(data)

    def progress(self, current: int, total: int, description: str = "") -> None:
        """Output progress indicator"""
        if self.verbosity >= OutputLevel.NORMAL.value:
            percentage = (current / total) * 100 if total > 0 else 0
            progress_bar = self._create_progress_bar(percentage)

            message = f"\r{progress_bar} {percentage:.1f}% {description}"
            self.output(message)

            if current >= total:
                self.output("")  # New line when complete

    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a text progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"

    def section(self, title: str) -> None:
        """Output section header"""
        if self.output_format == "json":
            self.json({"section": title})
        else:
            self.info(f"\n{title}")
            self.info("=" * len(title))

    def subsection(self, title: str) -> None:
        """Output subsection header"""
        if self.output_format == "json":
            self.json({"subsection": title})
        else:
            self.info(f"\n{title}")
            self.info("-" * len(title))

    def list_items(self, items: list, title: str = "") -> None:
        """Output list of items"""
        if title:
            self.subsection(title)

        if self.output_format == "json":
            self.json({"items": items})
        else:
            for i, item in enumerate(items, 1):
                self.info(f"  {i}. {item}")

    def key_value(self, key: str, value: Any) -> None:
        """Output key-value pair"""
        if self.output_format == "json":
            self.json({key: value})
        else:
            self.info(f"  {key}: {value}")

    def code_block(self, code: str, language: str = "") -> None:
        """Output code block"""
        if self.output_format == "json":
            self.json({"code": code, "language": language})
        else:
            if language:
                self.info(f"```{language}")
            else:
                self.info("```")
            self.info(code)
            self.info("```")

    def print_text(self, text: str) -> None:
        """Print plain text without formatting"""
        self.output(text)

    def print_header(self, message: str) -> None:
        """Print header message"""
        formatted = self._format_message(f"\n=== {message} ===", "info")
        print(formatted)

    def print_success(self, message: str) -> None:
        """Print success message"""
        formatted = self._format_message(f"✅ {message}", "success")
        print(formatted)

    def print_warning(self, message: str) -> None:
        """Print warning message"""
        formatted = self._format_message(f"⚠️ {message}", "warning")
        print(formatted)

    def print_error(self, message: str) -> None:
        """Print error message"""
        formatted = self._format_message(f"❌ {message}", "error")
        print(formatted)

    def print_info(self, message: str) -> None:
        """Print info message"""
        formatted = self._format_message(f"ℹ️ {message}", "info")
        print(formatted)
