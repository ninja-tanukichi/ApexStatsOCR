"""
build_dashboard_with_data()のプレースホルダ置換挙動のテスト。
"""
import json

from main import build_dashboard_with_data


def test_embeds_csv_text_as_valid_json(tmp_path):
    template_path = tmp_path / "template.html"
    template_path.write_text(
        '<script id="embedded-data" type="application/json">null</script>',
        encoding="utf-8",
    )
    output_path = tmp_path / "output.html"

    csv_text = "season,career_games\n1,100\n"
    build_dashboard_with_data(str(template_path), csv_text, str(output_path))

    html = output_path.read_text(encoding="utf-8")
    payload = html.split(">", 1)[1].rsplit("</script>", 1)[0]
    assert json.loads(payload) == csv_text


def test_escapes_closing_script_tag_in_csv_text(tmp_path):
    template_path = tmp_path / "template.html"
    template_path.write_text(
        '<script id="embedded-data" type="application/json">null</script>',
        encoding="utf-8",
    )
    output_path = tmp_path / "output.html"

    csv_text = "season,note\n1,</script><script>alert(1)</script>\n"
    build_dashboard_with_data(str(template_path), csv_text, str(output_path))

    html = output_path.read_text(encoding="utf-8")
    assert "<script>alert(1)</script>" not in html
