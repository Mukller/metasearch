import argparse
from metasearch.app import app


def main():
    parser = argparse.ArgumentParser(prog="metasearch", description="Self-hosted поисковый агрегатор")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    print(f"metasearch запущен на http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
