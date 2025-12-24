import csv
import io
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select

from database.connection import async_session
from database.models import Spike, SpikePost, Post, Channel

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{alert_id}")
async def export_alert(alert_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Spike).where(Spike.id == alert_id)
        )
        spike = result.scalar_one_or_none()

        if not spike:
            raise HTTPException(status_code=404, detail="Alert not found")

        channel_result = await session.execute(
            select(Channel).where(Channel.id == spike.channel_id)
        )
        channel = channel_result.scalar_one_or_none()

        posts_result = await session.execute(
            select(Post)
            .join(SpikePost)
            .where(SpikePost.spike_id == spike.id)
            .order_by(Post.toxicity_score.desc())
        )
        posts = posts_result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["HateWatch Evidence Export"])
        writer.writerow([f"Generated: {datetime.utcnow().isoformat()}"])
        writer.writerow([])

        writer.writerow(["Alert Summary"])
        writer.writerow(["Alert ID", spike.id])
        writer.writerow(["Channel", channel.username if channel else "N/A"])
        writer.writerow(["Country", spike.country or "N/A"])
        writer.writerow(["Severity", spike.severity])
        writer.writerow(["Spike Percentage", f"{spike.spike_percentage:.1f}%"])
        writer.writerow(["Baseline Toxicity", f"{spike.baseline_avg:.3f}" if spike.baseline_avg else "N/A"])
        writer.writerow(["Spike Toxicity", f"{spike.spike_avg:.3f}" if spike.spike_avg else "N/A"])
        writer.writerow(["Start Time", spike.spike_start.isoformat()])
        writer.writerow(["Total Posts", spike.post_count])
        writer.writerow([])

        writer.writerow(["Posts"])
        writer.writerow([
            "Post ID",
            "Posted At",
            "Text",
            "Toxicity Score",
            "Severe Toxicity",
            "Identity Attack",
            "Insult",
            "Threat",
            "Views",
            "Forwards"
        ])

        for post in posts:
            writer.writerow([
                post.telegram_message_id,
                post.posted_at.isoformat(),
                post.text.replace("\n", " "),
                f"{post.toxicity_score:.3f}" if post.toxicity_score else "",
                f"{post.severe_toxicity_score:.3f}" if post.severe_toxicity_score else "",
                f"{post.identity_attack_score:.3f}" if post.identity_attack_score else "",
                f"{post.insult_score:.3f}" if post.insult_score else "",
                f"{post.threat_score:.3f}" if post.threat_score else "",
                post.views or "",
                post.forwards or ""
            ])

        output.seek(0)

        filename = f"hatewatch_alert_{alert_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
