CREATE DATABASE IF NOT EXISTS device_analytics;

use device_analytics;

CREATE TABLE IF NOT EXISTS report_daily (
    device_id String,
    window_start DateTime64(3, 'UTC'),
    avg_heart_rate Float64,
)
ENGINE = ReplacingMergeTree()
ORDER BY (device_id, window_start);