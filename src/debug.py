from video_converter import gui
from video_converter.conveter import to_mp4
from video_converter.utils import cli_wrapper


def main():
    # gui.open_window()

    # to_mp4_wrapped = cli_wrapper(to_mp4)
    # to_mp4_wrapped(path="E:/datasets/iPhone/wakayama/IMG_1006.MOV")
    to_mp4(path="C:/Users/applejxd/src/DLServer/download/midv-433.ts").run()


if __name__ == "__main__":
    main()
