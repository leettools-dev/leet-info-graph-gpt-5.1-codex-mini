from __future__ import annotations

import os
import textwrap
import time
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from infograph.core.schemas import InfographicCreate, ResearchSession, Source
from infograph.stores.abstract_infographic_store import AbstractInfographicStore
from infograph.stores.duckdb.infographic_store_duckdb import InfographicStoreDuckDB
from infograph.stores.duckdb.utils import ensure_duckdb_settings
from leettools.settings import SystemSettings


class InfographicService:
    """Generate infographic artwork from a research session."""

    def __init__(
        self,
        store: AbstractInfographicStore | None = None,
        settings: SystemSettings | None = None,
    ) -> None:
        self.settings = ensure_duckdb_settings(settings)
        self.store = store or InfographicStoreDuckDB(self.settings)

        default_output = Path(self.settings.DATA_ROOT) / "infographics"
        self.output_dir = Path(os.environ.get("INFOGRAPHIC_PATH", default_output))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_for_session(
        self, session: ResearchSession, sources: Sequence[Source]
    ) -> InfographicCreate:
        """Build an infographic image and persist metadata."""
        key_points = self._build_key_points(sources)
        source_count = len(sources)
        layout_data = {
            "title": session.prompt,
            "key_points": key_points,
            "source_count": source_count,
        }

        image_path = self._render_image(session.prompt, key_points, source_count)

        payload = InfographicCreate(
            session_id=session.session_id,
            template_type="basic",
            image_path=str(image_path),
            layout_data=layout_data,
        )

        return await self.store.create(payload)

    def _build_key_points(self, sources: Sequence[Source]) -> list[str]:
        points: list[str] = []
        for source in sources[:4]:
            snippet = source.snippet.strip()
            if not snippet and source.title:
                points.append(source.title)
                continue

            sentence = snippet.split(".")[0].strip()
            points.append(sentence or snippet)
        if not points:
            points.append("AI-generated insight")
        return points

    def _render_image(self, title: str, key_points: list[str], source_count: int) -> Path:
        width = 1000
        height = 700
        background = (14, 23, 42)
        accent = (14, 165, 233)
        text_color = (248, 250, 252)

        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        padding = 40
        current_y = padding

        draw.text((padding, current_y), "Research Infograph", font=font, fill=accent)
        current_y += 30

        draw.text((padding, current_y), title, font=font, fill=text_color)
        current_y += 40

        draw.line((padding, current_y, width - padding, current_y), fill=accent, width=2)
        current_y += 20

        draw.text(
            (padding, current_y),
            f"Sources: {source_count}",
            font=font,
            fill=text_color,
        )
        current_y += 30

        for point in key_points:
            wrapped = textwrap.wrap(point, width=50)
            for line in wrapped:
                draw.text((padding, current_y), f"• {line}", font=font, fill=text_color)
                current_y += 25
            current_y += 5

        timestamp = time.time_ns()
        filename = f"infographic-{timestamp}.png"
        path = self.output_dir / filename
        image.save(path)
        return path
