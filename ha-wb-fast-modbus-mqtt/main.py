import argparse
import json
import os

from webui.app.main import app


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="Fast Modbus")
    parser.add_argument("--options", type=str, help="Путь до options.json")

    args = parser.parse_args()
    path_to_options = args.options

    app.ports = []
    try:
        with open(path_to_options, "r", encoding="utf-8") as f:
            data = json.load(f)
        for config in data["Serial port config"]:
            app.ports.append(config["Port"])
    except Exception as e:
        print(f"Ошибка при чтении конфигурации портов: {e}")

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
