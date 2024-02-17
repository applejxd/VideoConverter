from video_converter import gui
from video_converter.conveter import to_mp4
from video_converter.utils import cli_wrapper


def main():
    # gui.open_window()

    to_mp4_wrapped = cli_wrapper(to_mp4)
    to_mp4_wrapped(path="E:/datasets/iPhone/wakayama/IMG_1006.MOV")
    # to_mp4(path="E:/datasets/iPhone/wakayama/IMG_1006.MOV").run()


if __name__ == "__main__":
    main()
