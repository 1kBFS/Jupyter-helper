import libtmux
import os
import tqdm
import random
import click

PORT = 2222


def connect_to_session(session_name: str):
    server = libtmux.Server()
    if not server.has_session(target_session=session_name):
        raise RuntimeWarning(f"There is no tmux-session with name {session_name}")
    session = server.sessions.get(session_name=session_name)
    return session


@click.group()
def cli():
    pass


@click.command()
@click.argument("num_users", type=click.INT)
@click.option("--base-dir", default="./", help="рабочая директория")
@click.option("--session-name", default="jupyter", help="название сессии")
def start(num_users, base_dir='./', session_name="jupyter"):
    """
    Запустить $num_users ноутбуков. У каждого рабочая директория $base_dir+$folder_num
    """
    if num_users < 0:
        raise ValueError("Number of notebooks is positive.")
    base_dir = base_dir + "/" if base_dir[-1] != '/' else base_dir
    if not os.path.exists(base_dir):
        raise ValueError("No such base directory. ")
    server = libtmux.Server()
    if server.has_session(target_session=session_name):
        raise RuntimeWarning("The session with jupyter notebooks is already running, the notebooks are deployed.")
    server.new_session(session_name=session_name, start_directory=base_dir)
    session = server.sessions.get(session_name=session_name)
    for i in tqdm.trange(num_users):
        if not os.path.exists(f"{base_dir}dir{i}"):
            os.makedirs(f"{base_dir}dir{i}")
        token = random.getrandbits(128)
        session.new_window(attach=False, window_name=f"notebook {i}",
                           window_shell=f"jupyter notebook --port {PORT + i} --no-browser --NotebookApp.token={token} --NotebookApp.notebook_dir={base_dir}dir{i}",
                           start_directory=f"{base_dir}dir{i}")
        click.echo(f"jupyter notebook number {i}: port {PORT + i}, token {token}")


@click.command()
@click.argument("num", type=click.INT)
@click.option("--session-name", default="jupyter", help="Названия tmux-сессии, в которой запущены окружения", type=click.STRING)
def stop(session_name, num):
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    @:param num: номер ноутбука, кот. можно убить
    """
    session = connect_to_session(session_name)
    session.kill_window(f"notebook {num}")


@click.command(name="stop_all")
@click.option("--session-name", default="jupyter", help="Названия tmux-сессии, в которой запущены окружения", type=click.STRING)
def stop_all(session_name):
    """
    @:param session_name: Названия tmux-сессии, в которой запущены окружения
    """
    session = connect_to_session(session_name)
    session.kill_session()


if __name__ == '__main__':
    cli.add_command(start)
    cli.add_command(stop)
    cli.add_command(stop_all)
    cli()
