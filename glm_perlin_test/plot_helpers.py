from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import Event, KeyEvent
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Slider

colors = [
    (48, 112, 183),
    (201, 92, 46),
    (228, 179, 69),
    (117, 52, 137),
    (109, 188, 233),
    (130, 171, 69),
]

lines_colormap = ListedColormap(np.array(colors) / 255)


# add key callback to the figure to move the slider with the arrow keys
def key_callback_for_slider(slider: Slider) -> Callable[[Event], None]:
    def key_callback(event: Event) -> None:
        if not isinstance(event, KeyEvent):
            return
        if event.key == "right":
            new_val = slider.val + 1
        elif event.key == "left":
            new_val = slider.val - 1
        elif event.key == "shift+right":
            new_val = slider.val + 10
        elif event.key == "shift+left":
            new_val = slider.val - 10
        else:
            return
        new_val = max(slider.valmin, min(slider.valmax, new_val))  # clamp
        slider.set_val(new_val)

    return key_callback


# set the figure to close on escape
def close_on_escape(event: Event) -> None:
    if not isinstance(event, KeyEvent):
        return
    if event.key == "escape":
        plt.close(event.canvas.figure)


global __fig
global __axs
__fig: plt.Figure | None = None
__axs: list[plt.Axes] | None = None


def set_figure_and_axes(fig: plt.Figure, axs: list[plt.Axes]) -> None:
    global __fig
    global __axs

    __fig, __axs = fig, axs


def get_figure_and_axes() -> tuple[plt.Figure, list[plt.Axes]]:
    global __fig
    global __axs

    if __fig is None or __axs is None:
        raise ValueError("figure and axes not set")

    return __fig, __axs


get = get_figure_and_axes
set = set_figure_and_axes


def light_gray_grid(ax: plt.Axes) -> None:
    ax.grid(True)
    ax.grid(which="major", linestyle="--", color="lightgray")
    ax.set_axisbelow(True)


def data_viewer(D: np.ndarray) -> None:
    """View a 2D array an image with a slider. The first two dimensions are interpreted as the image XY. The last
    dimension is used for the slider."""

    def setup(*args: Any, **kwargs: Any) -> None:
        fig, axs = plt.subplots(1, 1, figsize=(10, 6))
        axs = [axs] if not isinstance(axs, list) else axs
        set(fig, axs)

        shape = D.shape

        if len(shape) != 3:
            raise ValueError("Data must be 3D")

        fig_data = {"shape": tuple(shape)}

        # Attach some extra data to the figure
        fig.data = fig_data  # type: ignore[attr-defined, unused-ignore]

        axs[0].set_xlim(0, shape[1])
        axs[0].set_ylim(np.min(D), np.max(D))

        # Create a slider to advance through the tvs
        ax_slider = plt.axes((0.1, 0.05, 0.80, 0.03))
        slider = Slider(ax_slider, "D.z", 0, D.shape[2] - 1, valinit=0, valstep=1)
        slider.on_changed(update)

        fig.canvas.mpl_connect("key_press_event", key_callback_for_slider(slider))
        fig.canvas.mpl_connect("key_press_event", close_on_escape)

    def update(index: Any) -> None:
        fig, axs = get()

        ax = axs[0]
        plt.sca(ax)
        ax.clear()

        im = D[:, :, int(index)]
        # cmap = lines_colormap
        cmap = "viridis"
        ax.imshow(im, cmap=cmap, interpolation="nearest", aspect="equal")

        # light_gray_grid(ax)

        fig_data = getattr(fig, "data", None)
        if fig_data is None:
            raise ValueError("fig.data not found")
        assert isinstance(fig_data, dict)
        shape: tuple[int, int, int] = fig_data["shape"]

        ax.set_xlim(0, shape[1])

        plt.draw()

    setup()
    update(0)
    plt.show()


def data_viewer_2(
    D1_in: tuple[np.ndarray, str],
    D2_in: tuple[np.ndarray, str],
    D3_in: tuple[np.ndarray, str],
    D4_in: tuple[np.ndarray, str],
    D5_in: tuple[np.ndarray, str],
    D6_in: tuple[np.ndarray, str],
) -> None:
    """View a 2D array an image with a slider. The first two dimensions are interpreted as the image XY. The last
    dimension is used for the slider."""

    D1, title1 = D1_in
    D2, title2 = D2_in
    D3, title3 = D3_in
    D4, title4 = D4_in
    D5, title5 = D5_in
    D6, title6 = D6_in

    if D1.shape != D2.shape:
        raise ValueError(
            f"Data shapes must match. D1.shape = {D1.shape}, D2.shape = {D2.shape}"
        )

    if D1.shape != D3.shape:
        raise ValueError(
            f"Data shapes must match. D1.shape = {D1.shape}, D3.shape = {D3.shape}"
        )

    if D1.shape != D4.shape:
        raise ValueError(
            f"Data shapes must match. D1.shape = {D1.shape}, D4.shape = {D4.shape}"
        )

    shape12 = D1.shape
    shape34 = D3.shape
    shape56 = D5.shape

    if len(shape12) != 3 or len(shape34) != 3 or len(shape56) != 3:
        raise ValueError("Data must be 3D")

    Zlen = shape12[2]

    if shape12[2] != shape34[2] or shape12[2] != shape56[2]:
        raise ValueError("shape12[2] must match shape34[2]")

    cmap = "viridis"

    def setup(*args: Any, **kwargs: Any) -> None:
        fig, axs = plt.subplots(3, 3, figsize=(8, 8))
        set(fig, axs)

        # Create a slider to advance through the tvs
        ax_slider = plt.axes((0.1, 0.05, 0.80, 0.03))
        slider = Slider(ax_slider, "D.z", 0, Zlen - 1, valinit=0, valstep=1)
        slider.on_changed(update)

        fig.canvas.mpl_connect("key_press_event", key_callback_for_slider(slider))
        fig.canvas.mpl_connect("key_press_event", close_on_escape)

    def _show_image(ax: plt.Axes, im: np.ndarray, name: str, title: str) -> None:
        ax.imshow(im, cmap=cmap, interpolation="nearest", aspect="equal")

        title = (
            title
            + "\n"
            + f"{im.mean():.2f} +/- {im.std():.2f}; <|{name}|> = {np.abs(im).mean():.2f}"
        )
        ax.set_title(title, fontsize=8)

    def update(index: Any) -> None:
        fig, axs = get()

        # === D1 ===

        ax = axs[0, 0]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D1[:, :, int(index)], "D1", title1)

        # === D2 ===

        ax = axs[0, 1]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D2[:, :, int(index)], "D2", title2)

        # === D12 = D1 - D2 ===

        ax = axs[0, 2]
        plt.sca(ax)
        ax.clear()
        im = D1[:, :, int(index)] - D2[:, :, int(index)]
        _show_image(ax, im, "D1 - D2", "")
        ax.set_title(f"max(|D1 - D2|) = \n{np.abs(im).max()}", fontsize=8)

        # === D3 ===

        ax = axs[1, 0]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D3[:, :, int(index)], "D3", title3)

        # === D4 ===

        ax = axs[1, 1]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D4[:, :, int(index)], "D4", title4)

        # === D34 = D3 - D4 ===

        ax = axs[1, 2]
        plt.sca(ax)
        ax.clear()
        im = D3[:, :, int(index)] - D4[:, :, int(index)]
        _show_image(ax, im, "D3 - D4", "")
        ax.set_title(f"max(|D3 - D4|) = \n{np.abs(im).max()}", fontsize=8)

        # === D5 ===

        ax = axs[2, 0]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D5[:, :, int(index)], "D5", title5)

        # === D6 ===

        ax = axs[2, 1]
        plt.sca(ax)
        ax.clear()
        _show_image(ax, D6[:, :, int(index)], "D6", title6)

        # === D56 = D5 - D6 ===

        ax = axs[2, 2]
        plt.sca(ax)
        ax.clear()
        im = D5[:, :, int(index)] - D6[:, :, int(index)]
        _show_image(ax, im, "D5 - D6", "")
        ax.set_title(f"max(|D5 - D6|) = \n{np.abs(im).max()}", fontsize=8)

        for ax in axs.flat:
            ax.set_xticks([])
            ax.set_yticks([])

        plt.draw()

    setup()
    update(0)
    plt.show()
