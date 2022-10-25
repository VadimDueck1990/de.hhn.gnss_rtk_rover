import nmeapoller_async
import uart_nmea


def start_app():
    print("running main")
    # nmeapoller_async.test()
    uart_nmea.test()


if __name__ == "__main__":
    start_app()
