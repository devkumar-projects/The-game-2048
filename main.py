from game.ui import Game2048App


def main() -> None:
    app = Game2048App()
    if app.winfo_exists():
        app.mainloop()


if __name__ == "__main__":
    main()
