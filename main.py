
from model import GameModel
from view import GameView
from controller import GameController


def main():
    model = GameModel()
    view = GameView(model)
    controller = GameController(model, view)

    controller.run()


if __name__ == "__main__":
    main()
