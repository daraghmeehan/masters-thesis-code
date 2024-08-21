from controller import Controller


def main():
    app_controller = Controller()
    app_controller.run()
    # TODO: Perhaps should do try block here to always clean temporary files.


if __name__ == "__main__":
    main()


### Testing using -i below!
# def main():
#     app_controller = Controller()
#     app_controller.run()
#     return app_controller


# if __name__ == "__main__":
#     controller = main()
