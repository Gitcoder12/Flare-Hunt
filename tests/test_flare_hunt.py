import io
import unittest

from flare_hunt import Hotspot, cluster_hotspots, haversine_km, load_firms_csv, parse_hotspot_row


class FlareHuntTests(unittest.TestCase):
    def test_parses_viirs_style_record_with_utc_time(self):
        row = {"latitude":"17.3850", "longitude":"78.4867", "acq_date":"2026-04-10", "acq_time":"0315", "frp":"4.2", "confidence":"h", "satellite":"N20", "version":"2.0NRT", "daynight":"N"}
        item = parse_hotspot_row(row, 2)
        self.assertEqual(item.confidence_class, "high")
        self.assertTrue(item.observed_at.endswith("+00:00"))
        self.assertEqual(item.frp_mw, 4.2)

    def test_invalid_coordinate_is_rejected(self):
        row = {"latitude":"91", "longitude":"0", "acq_date":"2026-01-01", "acq_time":"0000", "frp":"1", "confidence":"n"}
        with self.assertRaises(ValueError):
            parse_hotspot_row(row, 2)

    def test_csv_parser_keeps_bad_rows_in_reject_list(self):
        csv_text = "latitude,longitude,acq_date,acq_time,frp,confidence\n17.3,78.4,2026-01-01,0300,2,nominal\n999,78.4,2026-01-01,0300,2,high\n"
        valid, rejected = load_firms_csv(io.StringIO(csv_text))
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["source_row"], 3)

    def test_nearby_hotspots_in_window_cluster_together(self):
        a = Hotspot(17.3850, 78.4867, "2026-04-10T03:00:00+00:00", 2.0, "nominal", None, "N20", "2.0NRT", "N", 2)
        b = Hotspot(17.3860, 78.4870, "2026-04-10T03:15:00+00:00", 3.0, "high", None, "N20", "2.0NRT", "N", 3)
        clusters = cluster_hotspots([a, b], radius_km=1.0, time_window_hours=1.0)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0]["hotspot_count"], 2)
        self.assertEqual(clusters[0]["total_frp_mw"], 5.0)

    def test_far_hotspots_remain_separate(self):
        a = Hotspot(0, 0, "2026-04-10T03:00:00+00:00", 2.0, "low", None, "N20", "v", "N", 2)
        b = Hotspot(20, 20, "2026-04-10T03:10:00+00:00", 3.0, "high", None, "N20", "v", "N", 3)
        self.assertEqual(len(cluster_hotspots([a, b], 1, 1)), 2)

    def test_time_window_prevents_cluster(self):
        a = Hotspot(17.3850, 78.4867, "2026-04-10T03:00:00+00:00", 2.0, "low", None, "N20", "v", "N", 2)
        b = Hotspot(17.3851, 78.4868, "2026-04-12T03:00:00+00:00", 3.0, "high", None, "N20", "v", "N", 3)
        self.assertEqual(len(cluster_hotspots([a, b], 1, 12)), 2)

    def test_haversine_zero_distance(self):
        a = Hotspot(0, 0, "2026-04-10T03:00:00+00:00", 1, "low", None, "", "", "", 2)
        self.assertAlmostEqual(haversine_km(a, a), 0.0)


if __name__ == "__main__":
    unittest.main()
