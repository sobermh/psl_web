import multiprocessing
from psl_backend.index import run_flask_app
from psl_socket.server import run_socket_app

if __name__ == '__main__':
    flask_thread = multiprocessing.Process(target=run_flask_app)
    flask_thread.start()

    pyqt_thread = multiprocessing.Process(target=run_socket_app)
    pyqt_thread.start()
    #
    flask_thread.join()
    pyqt_thread.join()