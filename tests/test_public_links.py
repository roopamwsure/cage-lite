from pathlib import Path

from cage_lite.ui import receipt_viewer_v1 as viewer


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_package_metadata_exposes_public_project_links():
    pyproject = (
        PROJECT_ROOT / "pyproject.toml"
    ).read_text(encoding="utf-8")

    assert 'version = "0.1.2"' in pyproject
    assert (
        'description = "Open-source reference implementation '
        'for CAGE Prebind Assurance at the business consequence '
        'boundary"'
        in pyproject
    )
    assert (
        '"Live Demo" = "https://cage-lite.streamlit.app/"'
        in pyproject
    )
    assert (
        '"CAGE-1 on arXiv" = '
        '"https://arxiv.org/abs/2607.03510"'
        in pyproject
    )
    assert (
        'Changelog = "https://github.com/roopamwsure/'
        'cage-lite/blob/main/CHANGELOG.md"'
        in pyproject
    )


def test_header_includes_public_project_links(monkeypatch):
    rendered_blocks = []

    monkeypatch.setattr(
        viewer,
        "html_block",
        rendered_blocks.append,
    )
    monkeypatch.setattr(
        viewer,
        "logo_html",
        lambda: '<div class="logo-fallback">C</div>',
    )

    viewer.render_header()

    assert len(rendered_blocks) == 1

    header = rendered_blocks[0]

    assert "CAGE-lite" in header
    assert (
        "Prebind assurance for AI-agent actions at the "
        "business consequence boundary."
        in header
    )
    assert (
        "https://github.com/roopamwsure/cage-lite"
        in header
    )
    assert "https://arxiv.org/abs/2607.03510" in header
    assert "https://pypi.org/project/cage-lite/" in header
    assert 'aria-label="Project links"' in header
    assert header.count('target="_blank"') == 3
    assert header.count('rel="noopener noreferrer"') == 3
