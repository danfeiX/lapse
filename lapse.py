import os
from PIL import Image
import argparse
from datetime import datetime
import time
import shutil
import ffmpeg

SHOULD_EXIT = False


def capture(target_filename, scale=0.5, quality=85):
    os.system("screencapture {}".format(target_filename + ".png"))
    im = Image.open(target_filename + ".png")
    osize = im.size
    im = im.resize((int(osize[0] * scale) // 2 * 2, int(osize[1] * scale) // 2 * 2))  # make sure size is even number
    im = im.convert("RGB")
    im.save(target_filename + ".jpg", quality=quality)
    os.remove(target_filename + ".png")
    print("capture to {}".format(target_filename))


def dump_video(image_dir, video_filename, fps):
    print("dumping video from {} to {}!".format(image_dir, video_filename))
    (
        ffmpeg
        .input(image_dir + "/*.jpg", pattern_type="glob", framerate=fps)
        .output(video_filename)
        .run()
    )


def get_image_dir(lapse_root_dir):
    now = datetime.now()

    im_dir_name = now.strftime("%m%d%Y_%H_%M_%S")
    im_dir = os.path.join(args.lapse_root_dir, im_dir_name)
    os.makedirs(im_dir)
    
    return im_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--lapse_root_dir', type=str, default="/Users/danfei/Desktop/lapse/", help="Root directory of the lapse images and videos")
    parser.add_argument("--scale", type=float, default=0.4, help="Image scale wrt the original resolution")
    parser.add_argument("--compress_quality", type=int, default=85, help="JPEG compression quality")
    parser.add_argument("--capture_rate", type=float, default=1, help="Screen capture frequency in hz")
    parser.add_argument("--video_interval", type=float, default=3600, help="How long to wait before dumping a video")
    parser.add_argument("--video_fps", type=int, default=10, help="FPS of the saved video")
    parser.add_argument("--keep_images", action="store_true", default=False, help="Whether to keep the original image files after dumping video")
    args = parser.parse_args()

    iter_interval = 1 / args.capture_rate

    curr_im_dir = None
    start_time = time.time()
    image_counter = 0

    while not SHOULD_EXIT:
        curr_iter_time = time.time()
        
        if curr_im_dir is None:
            curr_im_dir = get_image_dir(args.lapse_root_dir)

        capture(
            curr_im_dir + "/" + str(image_counter).zfill(6),
            scale=args.scale,
            quality=args.compress_quality
        )

        image_counter += 1

        if time.time() - start_time > args.video_interval:
            dump_video(curr_im_dir, curr_im_dir.rstrip("/") + ".mp4", args.video_fps)

            if not args.keep_images:
                shutil.rmtree(curr_im_dir)
            # reset screen capture dir, time, and counter
            image_counter = 0
            start_time = time.time()
            curr_im_dir = None

        time_to_sleep = iter_interval - (time.time() - curr_iter_time)
        if time_to_sleep > 0:
            time.sleep(time_to_sleep)
