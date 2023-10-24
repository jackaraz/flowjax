import equinox as eqx
import jax.numpy as jnp
import jax.random as jr
import pytest
from jax import tree_map, vmap

from flowjax.bijections import RationalQuadraticSpline


def test_RationalQuadraticSpline_tails():
    key = jr.PRNGKey(0)
    x = jnp.array([-20, 0.1, 2, 20])
    spline = RationalQuadraticSpline(knots=10, interval=3)

    # Change to random initialisation, rather than identity.
    spline = tree_map(
        lambda x: jr.normal(key, x.shape) if eqx.is_inexact_array(x) else x,
        spline,
    )

    y = vmap(spline.transform)(x)
    expected_changed = jnp.array([True, False, False, True])  # identity padding
    assert ((jnp.abs(y - x) <= 1e-5) == expected_changed).all()


def test_RationalQuadraticSpline_init():
    # Test it is initialised at the identity
    x = jnp.array([-1, 0.1, 2, 1])
    key = jr.PRNGKey(0)
    spline = RationalQuadraticSpline(knots=10, interval=3)
    y = vmap(spline.transform)(x)
    assert pytest.approx(x, abs=1e-6) == y

    shape = spline.unbounded_derivatives.shape
    spline = eqx.tree_at(
        lambda b: b.unbounded_derivatives,
        spline,
        jr.normal(key, shape),
    )
    y = spline.transform(x)
    assert pytest.approx(x, abs=1e-6) != y
