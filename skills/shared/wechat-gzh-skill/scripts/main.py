import argparse
import json
import re
import sys
from pathlib import Path

from config import load_config
from converter import convert_article, MarkdownConverter
from markdown_parser import parse_markdown
from themes import list_themes
from wechat_api import WechatAPI, WechatAPIError


def main():
    parser = argparse.ArgumentParser(
        description="微信公众号草稿发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    publish_parser = subparsers.add_parser("publish", help="转换 Markdown 并发布到草稿箱")
    publish_parser.add_argument("file", help="Markdown 文件路径")
    publish_parser.add_argument("--theme", default="default", help="主题名称")
    publish_parser.add_argument("--cover", help="封面图路径（可选）")
    publish_parser.add_argument("--dry-run", action="store_true", help="仅转换不发布")

    convert_parser = subparsers.add_parser("convert", help="仅转换 Markdown 为 HTML")
    convert_parser.add_argument("file", help="Markdown 文件路径")
    convert_parser.add_argument("--theme", default="default", help="主题名称")
    convert_parser.add_argument("--output", help="输出文件路径（可选）")

    themes_parser = subparsers.add_parser("themes", help="列出可用主题")

    config_parser = subparsers.add_parser("config", help="检查配置")
    config_parser.add_argument("action", choices=["check"], help="检查环境变量配置")

    args = parser.parse_args()

    if args.command == "themes":
        result = {"success": True, "themes": list_themes()}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == "config":
        if args.action == "check":
            try:
                config = load_config()
                result = {
                    "success": True,
                    "appid": config.appid[:8] + "***",
                    "secret": "***",
                    "message": "配置正常",
                }
            except ValueError as e:
                result = {"success": False, "error": str(e)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == "convert":
        try:
            article = parse_markdown(args.file)
            theme = args.theme or article.metadata.theme
            html = convert_article(article, theme)

            if args.output:
                Path(args.output).write_text(html, encoding="utf-8")
                result = {
                    "success": True,
                    "output": args.output,
                    "title": article.metadata.title,
                    "theme": theme,
                    "content_length": len(html),
                }
            else:
                result = {
                    "success": True,
                    "html": html,
                    "title": article.metadata.title,
                    "theme": theme,
                    "content_length": len(html),
                }

            print(json.dumps(result, ensure_ascii=False, indent=2))
        except FileNotFoundError as e:
            result = {"success": False, "error": str(e)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
        except Exception as e:
            result = {"success": False, "error": str(e)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
        return

    if args.command == "publish":
        try:
            config = load_config()
            api = WechatAPI(config)

            article = parse_markdown(args.file)
            theme = args.theme or article.metadata.theme
            
            converter = MarkdownConverter(theme)
            html = converter.convert(article)
            
            table_images = converter.table_images

            if args.dry_run:
                result = {
                    "success": True,
                    "dry_run": True,
                    "title": article.metadata.title,
                    "theme": theme,
                    "content_length": len(html),
                    "images": len(article.images),
                    "tables": len(table_images),
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return

            uploaded_images = []
            for img in article.images:
                if img.is_local:
                    upload_result = api.upload_image(img.original)
                    img.wechat_url = upload_result.url
                    uploaded_images.append({
                        "original": img.original,
                        "wechat_url": upload_result.url,
                    })

            for idx, table_img_path in enumerate(table_images):
                upload_result = api.upload_image(table_img_path)
                placeholder = f"TABLE_IMG_PLACEHOLDER_{idx}"
                html = html.replace(placeholder, upload_result.url)
                uploaded_images.append({
                    "original": f"table_{idx}",
                    "wechat_url": upload_result.url,
                })

            cover_path = args.cover or article.metadata.cover
            if not cover_path and article.images:
                first_img = article.images[0]
                if first_img.is_local:
                    cover_path = first_img.original

            if not cover_path:
                result = {
                    "success": False,
                    "error": "未找到封面图，请通过 --cover 参数指定或在 frontmatter 中设置 cover",
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
                sys.exit(1)

            cover_result = api.upload_material(cover_path)

            draft_result = api.create_draft(
                title=article.metadata.title,
                content=html,
                thumb_media_id=cover_result.media_id,
                author=article.metadata.author,
                digest=article.metadata.digest,
            )

            result = {
                "success": True,
                "media_id": draft_result.media_id,
                "title": article.metadata.title,
                "theme": theme,
                "images_uploaded": len(uploaded_images),
                "tables_converted": len(table_images),
                "content_length": len(html),
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))

        except FileNotFoundError as e:
            result = {"success": False, "error": str(e)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
        except WechatAPIError as e:
            result = {"success": False, "error": f"微信 API 错误: [{e.errcode}] {e.errmsg}"}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
        except Exception as e:
            result = {"success": False, "error": str(e)}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            sys.exit(1)
        return

    parser.print_help()


if __name__ == "__main__":
    main()