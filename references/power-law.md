# Power-law fitting

Use this reference only when the user asks for scaling or a power-law fit.

## Method

Fit positive observations to

\[
y = a x^b
\]

with ordinary least squares in log-log space:

```python
log_x = np.log(np.asarray(x, dtype=float))
log_y = np.log(np.asarray(y, dtype=float))
exponent, log_prefactor = np.polyfit(log_x, log_y, 1)
prefactor = np.exp(log_prefactor)
```

Compute log-space goodness of fit:

```python
fitted_log_y = log_prefactor + exponent * log_x
r2_log = 1.0 - np.sum((log_y - fitted_log_y) ** 2) / np.sum(
    (log_y - log_y.mean()) ** 2
)
```

## Plotting rules

- Fit only the points the user names. Never silently include a held-out or extrapolation point.
- Generate the smooth curve with `np.geomspace` across the displayed x-range.
- Draw the fit with light gray `#A3A8AE`, a thin dash-dot line, and lower visual priority than observations.
- Label it clearly, for example `MAE fit (first 4)`.
- Use a filled marker for fitted observations and an open marker for an explicitly excluded comparison point when that distinction matters.
- Keep the extrapolated endpoint inside the visible y-limits.
- Apply the fit only to the requested metric. Do not fit RMSE merely because it appears in the same panel.
- Report `b`, log-space `R²`, and any extrapolated value outside the figure when useful.

## Interpretation guardrail

Treat a fit over three or four observations as descriptive. State that extrapolation may fail or flatten, especially when the held-out observation deviates materially from the fitted curve.
