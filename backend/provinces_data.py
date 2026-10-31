# -*- coding: utf-8 -*-
"""
Master 34 Provinces Data for Backend Service
"""

PROVINCES_34 = [
    {"id": "VN_HN", "name": "Hà Nội", "province": "Hà Nội", "region": "Miền Bắc", "type": "Thành phố", "lat": 21.0285, "lon": 105.8542,
     "condition": "partly_cloudy", "weather_text": "Mây thay đổi, trời hanh khô", "temp": 22.4, "feels_like": 23.0, "humidity": 72, "wind_speed": 3.2, "wind_dir": "Đông Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 4.5, "pressure": 1014, "visibility": 9.0, "pm25": 38.5, "pm10": 58.2, "no2": 21.4, "co": 0.82, "o3": 18.5, "so2": 6.4,
     "outdoor_activities": ["Đi dạo", "Chụp ảnh", "Du lịch"], "outdoor_score": 82, "best_time": "08:30 - 11:00, 14:30 - 17:30", "outdoor_advice": "Thời tiết dễ chịu, thích hợp tham quan phố cổ, hồ Gươm; sáng sớm nên đeo khẩu trang do bụi tích tụ."},
    
    {"id": "VN_HP", "name": "Hải Phòng", "province": "Hải Phòng", "region": "Miền Bắc", "type": "Thành phố", "lat": 20.8449, "lon": 106.6881,
     "condition": "cloudy", "weather_text": "Nhiều mây, gió biển nhẹ", "temp": 23.0, "feels_like": 23.8, "humidity": 78, "wind_speed": 4.5, "wind_dir": "Đông Bắc",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 4.0, "pressure": 1013, "visibility": 10.0, "pm25": 32.0, "pm10": 51.5, "no2": 23.4, "co": 0.86, "o3": 20.2, "so2": 7.5,
     "outdoor_activities": ["Du lịch", "Đi dạo", "Chụp ảnh"], "outdoor_score": 85, "best_time": "08:00 - 11:30, 15:00 - 18:00", "outdoor_advice": "Gió mát ven biển, thích hợp khám phá ẩm thực và dạo phố đi bộ Tam Bạc."},
    
    {"id": "VN_HUE", "name": "Huế", "province": "Thừa Thiên Huế", "region": "Miền Trung", "type": "Thành phố", "lat": 16.4637, "lon": 107.5909,
     "condition": "light_rain", "weather_text": "Mưa rào nhẹ rải rác, se lạnh", "temp": 24.0, "feels_like": 24.5, "humidity": 85, "wind_speed": 2.8, "wind_dir": "Đông",
     "rain_prob": 65, "rain_mm": 3.5, "uv": 2.5, "pressure": 1012, "visibility": 7.5, "pm25": 16.2, "pm10": 26.8, "no2": 12.0, "co": 0.42, "o3": 29.5, "so2": 3.2,
     "outdoor_activities": ["Tham quan", "Chụp ảnh"], "outdoor_score": 68, "best_time": "09:00 - 11:30", "outdoor_advice": "Có mưa bay lãng mạn xứ Huế, thích hợp tham quan Đại Nội, chùa Thiên Mụ kèm ô/áo mưa mỏng."},
    
    {"id": "VN_DN", "name": "Đà Nẵng", "province": "Đà Nẵng", "region": "Miền Trung", "type": "Thành phố", "lat": 16.0544, "lon": 108.2022,
     "condition": "sunny", "weather_text": "Trời nắng ráo, biển êm, gió lộng", "temp": 27.5, "feels_like": 28.5, "humidity": 70, "wind_speed": 4.2, "wind_dir": "Đông",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 7.2, "pressure": 1012, "visibility": 12.0, "pm25": 14.5, "pm10": 24.0, "no2": 11.5, "co": 0.40, "o3": 34.0, "so2": 3.2,
     "outdoor_activities": ["Đi biển", "Chạy bộ", "Picnic", "Đạp xe", "Du lịch"], "outdoor_score": 96, "best_time": "06:00 - 09:00, 15:30 - 18:30", "outdoor_advice": "Thời tiết lý tưởng bậc nhất toàn quốc! Rất phù hợp tắm biển Mỹ Khê, đạp xe cầu Rồng, dã ngoại Sơn Trà."},
    
    {"id": "VN_HCM", "name": "Thành phố Hồ Chí Minh", "province": "Thành phố Hồ Chí Minh", "region": "Miền Nam", "type": "Thành phố", "lat": 10.7769, "lon": 106.7009,
     "condition": "partly_cloudy", "weather_text": "Nắng gián đoạn, chiều tối thoáng mát", "temp": 31.5, "feels_like": 34.0, "humidity": 66, "wind_speed": 3.0, "wind_dir": "Nam - Đông Nam",
     "rain_prob": 20, "rain_mm": 0.0, "uv": 8.0, "pressure": 1010, "visibility": 10.0, "pm25": 31.5, "pm10": 51.0, "no2": 24.6, "co": 0.95, "o3": 26.4, "so2": 4.8,
     "outdoor_activities": ["Đi dạo", "Chạy bộ", "Picnic", "Chụp ảnh"], "outdoor_score": 80, "best_time": "06:30 - 08:30, 16:30 - 21:00", "outdoor_advice": "Buổi trưa nắng gắt (UV 8), nên dạo chơi công viên bờ sông Sài Gòn, phố đi bộ Nguyễn Huệ vào buổi chiều tối."},
    
    {"id": "VN_CT", "name": "Cần Thơ", "province": "Cần Thơ", "region": "Miền Nam", "type": "Thành phố", "lat": 10.0452, "lon": 105.7469,
     "condition": "sunny", "weather_text": "Nắng ấm miền Tây, gió sông dịu mát", "temp": 30.2, "feels_like": 32.5, "humidity": 72, "wind_speed": 2.8, "wind_dir": "Đông Nam",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 7.5, "pressure": 1011, "visibility": 11.0, "pm25": 21.4, "pm10": 36.8, "no2": 15.2, "co": 0.58, "o3": 24.6, "so2": 3.8,
     "outdoor_activities": ["Du lịch", "Tham quan", "Picnic"], "outdoor_score": 88, "best_time": "06:00 - 09:30, 16:00 - 19:00", "outdoor_advice": "Thời tiết tuyệt vời để tham quan chợ nổi Cái Răng sáng sớm, dạo bến Ninh Kiều về đêm."},

    {"id": "VN_CB", "name": "Cao Bằng", "province": "Cao Bằng", "region": "Miền Bắc", "type": "Tỉnh", "lat": 22.6667, "lon": 106.2500,
     "condition": "foggy", "weather_text": "Sương mù buổi sáng, trưa hửng nắng nhẹ", "temp": 17.5, "feels_like": 17.5, "humidity": 84, "wind_speed": 2.0, "wind_dir": "Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 3.5, "pressure": 1016, "visibility": 6.5, "pm25": 15.0, "pm10": 24.5, "no2": 8.5, "co": 0.35, "o3": 31.0, "so2": 2.5,
     "outdoor_activities": ["Leo núi", "Du lịch", "Chụp ảnh"], "outdoor_score": 86, "best_time": "09:30 - 15:30", "outdoor_advice": "Thời tiết trong trẻo mát lạnh, rất thích hợp check-in thác Bản Giốc, suối Lê-nin; cần áo ấm."},

    {"id": "VN_TQ", "name": "Tuyên Quang", "province": "Tuyên Quang", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.8233, "lon": 105.2153,
     "condition": "partly_cloudy", "weather_text": "Mây rải rác, không khí thoáng đãng", "temp": 21.0, "feels_like": 21.5, "humidity": 76, "wind_speed": 2.2, "wind_dir": "Đông Bắc",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 4.5, "pressure": 1015, "visibility": 9.5, "pm25": 22.1, "pm10": 35.4, "no2": 13.5, "co": 0.52, "o3": 25.0, "so2": 4.1,
     "outdoor_activities": ["Du lịch", "Dã ngoại", "Picnic"], "outdoor_score": 84, "best_time": "08:30 - 16:30", "outdoor_advice": "Khí hậu hồ Na Hang mát mẻ, thích hợp du thuyền ngắm cảnh thiên nhiên sơn thủy."},

    {"id": "VN_DB", "name": "Điện Biên", "province": "Điện Biên", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.3860, "lon": 103.0230,
     "condition": "sunny", "weather_text": "Nắng vàng hanh hao, trời trong xanh", "temp": 20.5, "feels_like": 20.5, "humidity": 68, "wind_speed": 2.5, "wind_dir": "Tây Bắc",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 5.0, "pressure": 1015, "visibility": 12.0, "pm25": 18.4, "pm10": 29.8, "no2": 10.2, "co": 0.41, "o3": 28.5, "so2": 3.0,
     "outdoor_activities": ["Tham quan", "Chụp ảnh", "Du lịch"], "outdoor_score": 90, "best_time": "08:00 - 16:00", "outdoor_advice": "Trời trong xanh không mưa, hoàn hảo để tham quan di tích Điện Biên Phủ, đồi A1."},

    {"id": "VN_LC", "name": "Lai Châu", "province": "Lai Châu", "region": "Miền Bắc", "type": "Tỉnh", "lat": 22.3964, "lon": 103.4589,
     "condition": "foggy", "weather_text": "Sương mờ giăng đèo, se lạnh vùng cao", "temp": 16.2, "feels_like": 16.0, "humidity": 86, "wind_speed": 2.1, "wind_dir": "Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 3.8, "pressure": 1017, "visibility": 6.0, "pm25": 12.0, "pm10": 19.5, "no2": 7.5, "co": 0.28, "o3": 35.0, "so2": 2.0,
     "outdoor_activities": ["Leo núi", "Chụp ảnh"], "outdoor_score": 83, "best_time": "10:00 - 15:00", "outdoor_advice": "Đèo Ô Quy Hồ săn mây tuyệt đẹp, lái xe cần chú ý sương mù ban sáng."},

    {"id": "VN_SL", "name": "Sơn La", "province": "Sơn La", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.3283, "lon": 103.9148,
     "condition": "sunny", "weather_text": "Nắng dịu cao nguyên, gió nhẹ mát lạnh", "temp": 18.5, "feels_like": 18.5, "humidity": 70, "wind_speed": 2.4, "wind_dir": "Bắc",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 5.2, "pressure": 1016, "visibility": 11.0, "pm25": 14.8, "pm10": 24.2, "no2": 9.1, "co": 0.36, "o3": 30.5, "so2": 2.8,
     "outdoor_activities": ["Picnic", "Chụp ảnh", "Du lịch"], "outdoor_score": 93, "best_time": "08:30 - 16:30", "outdoor_advice": "Khí hậu Mộc Châu trong lành tuyệt đối, lý tưởng để tham quan đồi chè, thác Dải Yếm."},

    {"id": "VN_LCA", "name": "Lào Cai", "province": "Lào Cai", "region": "Miền Bắc", "type": "Tỉnh", "lat": 22.4856, "lon": 103.9707,
     "condition": "foggy", "weather_text": "Sương mây bồng bềnh Sa Pa, rét nhẹ", "temp": 14.5, "feels_like": 14.0, "humidity": 88, "wind_speed": 2.6, "wind_dir": "Bắc",
     "rain_prob": 20, "rain_mm": 0.0, "uv": 3.0, "pressure": 1018, "visibility": 5.5, "pm25": 13.5, "pm10": 21.8, "no2": 8.0, "co": 0.30, "o3": 33.2, "so2": 2.2,
     "outdoor_activities": ["Du lịch", "Leo núi", "Chụp ảnh"], "outdoor_score": 88, "best_time": "10:30 - 15:30", "outdoor_advice": "Sa Pa mờ sương lãng mạn, thích hợp trekking bản Cát Cát, cáp treo Fansipan."},

    {"id": "VN_TN", "name": "Thái Nguyên", "province": "Thái Nguyên", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.5942, "lon": 105.8482,
     "condition": "partly_cloudy", "weather_text": "Mây mỏng, nắng ấm hồ Núi Cốc", "temp": 22.0, "feels_like": 22.5, "humidity": 74, "wind_speed": 2.5, "wind_dir": "Đông Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 4.6, "pressure": 1014, "visibility": 9.0, "pm25": 28.5, "pm10": 45.2, "no2": 18.5, "co": 0.72, "o3": 21.0, "so2": 5.8,
     "outdoor_activities": ["Đi dạo", "Picnic", "Du lịch"], "outdoor_score": 83, "best_time": "08:00 - 11:00, 14:00 - 17:00", "outdoor_advice": "Thời tiết đẹp để cắm trại hồ Núi Cốc, tham quan không gian trà Tân Cương."},

    {"id": "VN_LS", "name": "Lạng Sơn", "province": "Lạng Sơn", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.8537, "lon": 106.7620,
     "condition": "overcast", "weather_text": "Trời âm u, gió mùa se lạnh biên giới", "temp": 18.0, "feels_like": 17.5, "humidity": 80, "wind_speed": 3.4, "wind_dir": "Đông Bắc",
     "rain_prob": 25, "rain_mm": 0.0, "uv": 2.8, "pressure": 1016, "visibility": 8.0, "pm25": 20.4, "pm10": 33.0, "no2": 11.8, "co": 0.48, "o3": 26.5, "so2": 3.5,
     "outdoor_activities": ["Tham quan", "Mua sắm"], "outdoor_score": 75, "best_time": "09:00 - 15:00", "outdoor_advice": "Trời lạnh hanh, thích hợp tham quan động Tam Thanh, chợ cửa khẩu Tân Thanh."},

    {"id": "VN_QN", "name": "Quảng Ninh", "province": "Quảng Ninh", "region": "Miền Bắc", "type": "Tỉnh", "lat": 20.9505, "lon": 107.0734,
     "condition": "partly_cloudy", "weather_text": "Gió vịnh Hạ Long lộng mát, trời trong", "temp": 23.5, "feels_like": 24.2, "humidity": 75, "wind_speed": 4.8, "wind_dir": "Đông Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 5.0, "pressure": 1013, "visibility": 11.0, "pm25": 19.8, "pm10": 32.5, "no2": 14.5, "co": 0.54, "o3": 28.0, "so2": 5.2,
     "outdoor_activities": ["Du thuyền", "Đi biển", "Chụp ảnh", "Du lịch"], "outdoor_score": 94, "best_time": "08:00 - 11:30, 14:00 - 17:30", "outdoor_advice": "Thời tiết tuyệt vời cho tour du thuyền vịnh Hạ Long, Bái Tử Long."},

    {"id": "VN_BN", "name": "Bắc Ninh", "province": "Bắc Ninh", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.1861, "lon": 106.0763,
     "condition": "partly_cloudy", "weather_text": "Nắng hanh Kinh Bắc, gió nhẹ", "temp": 22.8, "feels_like": 23.2, "humidity": 73, "wind_speed": 2.7, "wind_dir": "Đông Bắc",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 4.5, "pressure": 1014, "visibility": 9.0, "pm25": 36.2, "pm10": 56.0, "no2": 22.0, "co": 0.85, "o3": 19.0, "so2": 6.8,
     "outdoor_activities": ["Tham quan", "Chụp ảnh"], "outdoor_score": 80, "best_time": "08:30 - 11:00, 14:30 - 17:00", "outdoor_advice": "Thích hợp vãn cảnh chùa Dâu, đền Đô; lưu ý mật độ phương tiện khu công nghiệp."},

    {"id": "VN_PT", "name": "Phú Thọ", "province": "Phú Thọ", "region": "Miền Bắc", "type": "Tỉnh", "lat": 21.3228, "lon": 105.2280,
     "condition": "sunny", "weather_text": "Nắng vàng đất Tổ, trời cao trong xanh", "temp": 22.5, "feels_like": 22.8, "humidity": 71, "wind_speed": 2.3, "wind_dir": "Đông",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 4.8, "pressure": 1014, "visibility": 10.5, "pm25": 24.5, "pm10": 39.0, "no2": 15.0, "co": 0.58, "o3": 23.5, "so2": 4.2,
     "outdoor_activities": ["Tham quan", "Dã ngoại", "Picnic"], "outdoor_score": 89, "best_time": "07:30 - 11:30, 14:00 - 17:00", "outdoor_advice": "Khí hậu mát mẻ, hoàn hảo để dâng hương đền Hùng, ngắm đồi chè Long Cốc."},

    {"id": "VN_HY", "name": "Hưng Yên", "province": "Hưng Yên", "region": "Miền Bắc", "type": "Tỉnh", "lat": 20.6560, "lon": 106.0510,
     "condition": "cloudy", "weather_text": "Mây bao phủ phố Hiến, thoáng đãng", "temp": 23.0, "feels_like": 23.5, "humidity": 76, "wind_speed": 3.0, "wind_dir": "Đông Bắc",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 4.0, "pressure": 1013, "visibility": 9.5, "pm25": 30.5, "pm10": 48.0, "no2": 19.5, "co": 0.76, "o3": 21.5, "so2": 5.4,
     "outdoor_activities": ["Đi dạo", "Tham quan"], "outdoor_score": 82, "best_time": "08:00 - 11:00, 15:00 - 17:30", "outdoor_advice": "Dạo hồ Bán Nguyệt, tham quan đền Chử Đồng Tử rất thư thái."},

    {"id": "VN_NB", "name": "Ninh Bình", "province": "Ninh Bình", "region": "Miền Bắc", "type": "Tỉnh", "lat": 20.2506, "lon": 105.9745,
     "condition": "partly_cloudy", "weather_text": "Nắng nhẹ Tràng An, gió mát non nước", "temp": 23.2, "feels_like": 23.8, "humidity": 74, "wind_speed": 3.1, "wind_dir": "Đông",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 5.0, "pressure": 1013, "visibility": 10.5, "pm25": 21.0, "pm10": 34.5, "no2": 13.0, "co": 0.50, "o3": 27.0, "so2": 4.0,
     "outdoor_activities": ["Du thuyền", "Đạp xe", "Chụp ảnh", "Du lịch"], "outdoor_score": 95, "best_time": "07:30 - 11:00, 14:00 - 17:00", "outdoor_advice": "Một trong những điểm đến ngoài trời tuyệt nhất hôm nay! Đạp xe Tam Cốc, chèo thuyền Tràng An."},

    {"id": "VN_TH", "name": "Thanh Hóa", "province": "Thanh Hóa", "region": "Miền Trung", "type": "Tỉnh", "lat": 19.8067, "lon": 105.7852,
     "condition": "sunny", "weather_text": "Nắng ấm ven biển Sầm Sơn, sóng êm", "temp": 24.5, "feels_like": 25.2, "humidity": 75, "wind_speed": 3.5, "wind_dir": "Đông",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 5.8, "pressure": 1013, "visibility": 11.0, "pm25": 23.0, "pm10": 37.0, "no2": 14.0, "co": 0.52, "o3": 26.0, "so2": 4.5,
     "outdoor_activities": ["Đi biển", "Đi dạo", "Chạy bộ"], "outdoor_score": 89, "best_time": "06:30 - 09:30, 15:00 - 18:00", "outdoor_advice": "Thời tiết Sầm Sơn rất đẹp, thích hợp dạo biển, tham quan hòn Trống Mái."},

    {"id": "VN_NA", "name": "Nghệ An", "province": "Nghệ An", "region": "Miền Trung", "type": "Tỉnh", "lat": 18.6734, "lon": 105.6813,
     "condition": "sunny", "weather_text": "Trời quang mây tạnh, gió Cửa Lò mát rượi", "temp": 25.0, "feels_like": 25.8, "humidity": 73, "wind_speed": 3.6, "wind_dir": "Đông",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 6.0, "pressure": 1013, "visibility": 11.5, "pm25": 20.5, "pm10": 33.5, "no2": 12.5, "co": 0.48, "o3": 29.0, "so2": 3.8,
     "outdoor_activities": ["Du lịch", "Tham quan", "Đi biển"], "outdoor_score": 91, "best_time": "07:00 - 10:00, 15:00 - 18:00", "outdoor_advice": "Tham quan quê Bác Nam Đàn và dạo bờ biển Cửa Lò với tiết trời lý tưởng."},

    {"id": "VN_HT", "name": "Hà Tĩnh", "province": "Hà Tĩnh", "region": "Miền Trung", "type": "Tỉnh", "lat": 18.3560, "lon": 105.9058,
     "condition": "partly_cloudy", "weather_text": "Mây trôi nhẹ nhàng ngã ba Đồng Lộc", "temp": 24.8, "feels_like": 25.4, "humidity": 76, "wind_speed": 3.2, "wind_dir": "Đông",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 5.5, "pressure": 1013, "visibility": 10.0, "pm25": 18.5, "pm10": 30.2, "no2": 11.0, "co": 0.44, "o3": 30.0, "so2": 3.5,
     "outdoor_activities": ["Tham quan", "Du lịch"], "outdoor_score": 87, "best_time": "07:30 - 10:30, 14:30 - 17:30", "outdoor_advice": "Khí hậu dịu mát, thích hợp viếng ngã ba Đồng Lộc, hồ Kẻ Gỗ."},

    {"id": "VN_QT", "name": "Quảng Trị", "province": "Quảng Trị", "region": "Miền Trung", "type": "Tỉnh", "lat": 16.7500, "lon": 107.1854,
     "condition": "cloudy", "weather_text": "Nhiều mây ven sông Thạch Hãn", "temp": 24.5, "feels_like": 25.0, "humidity": 82, "wind_speed": 3.0, "wind_dir": "Đông",
     "rain_prob": 30, "rain_mm": 0.5, "uv": 4.2, "pressure": 1012, "visibility": 9.0, "pm25": 16.0, "pm10": 26.5, "no2": 9.8, "co": 0.38, "o3": 31.5, "so2": 3.0,
     "outdoor_activities": ["Tham quan", "Lịch sử"], "outdoor_score": 80, "best_time": "08:00 - 11:00, 14:30 - 17:00", "outdoor_advice": "Trời mát, thích hợp tham quan Thành cổ Quảng Trị, địa đạo Vịnh Mốc."},

    {"id": "VN_QNG", "name": "Quảng Ngãi", "province": "Quảng Ngãi", "region": "Miền Trung", "type": "Tỉnh", "lat": 15.1205, "lon": 108.7923,
     "condition": "sunny", "weather_text": "Nắng vàng biển đảo Lý Sơn, biển lặng", "temp": 26.5, "feels_like": 27.5, "humidity": 72, "wind_speed": 3.8, "wind_dir": "Đông Nam",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 6.8, "pressure": 1012, "visibility": 12.0, "pm25": 15.2, "pm10": 25.0, "no2": 10.5, "co": 0.40, "o3": 33.0, "so2": 3.2,
     "outdoor_activities": ["Đi biển", "Du lịch", "Chụp ảnh"], "outdoor_score": 93, "best_time": "06:30 - 09:30, 15:30 - 18:30", "outdoor_advice": "Tàu ra đảo Lý Sơn thuận lợi, biển êm đềm, check-in cổng Tò Vò hoàng hôn."},

    {"id": "VN_GL", "name": "Gia Lai", "province": "Gia Lai", "region": "Miền Trung", "type": "Tỉnh", "lat": 13.9833, "lon": 108.0000,
     "condition": "sunny", "weather_text": "Nắng vàng Biển Hồ Pleiku lộng gió", "temp": 23.5, "feels_like": 23.5, "humidity": 65, "wind_speed": 3.5, "wind_dir": "Đông Bắc",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 7.0, "pressure": 1014, "visibility": 13.0, "pm25": 11.5, "pm10": 19.0, "no2": 7.2, "co": 0.28, "o3": 36.0, "so2": 2.2,
     "outdoor_activities": ["Picnic", "Chụp ảnh", "Đạp xe", "Du lịch"], "outdoor_score": 96, "best_time": "07:00 - 10:30, 15:00 - 18:00", "outdoor_advice": "Không khí cao nguyên sạch sẽ bậc nhất Việt Nam! Rất lý tưởng dạo Biển Hồ, núi lửa Chư Đăng Ya."},

    {"id": "VN_KH", "name": "Khánh Hòa", "province": "Khánh Hòa", "region": "Miền Trung", "type": "Tỉnh", "lat": 12.2388, "lon": 109.1967,
     "condition": "sunny", "weather_text": "Trời trong xanh biển Nha Trang, nắng đẹp", "temp": 28.0, "feels_like": 29.5, "humidity": 69, "wind_speed": 4.0, "wind_dir": "Đông",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 7.5, "pressure": 1011, "visibility": 12.0, "pm25": 13.8, "pm10": 23.2, "no2": 11.0, "co": 0.39, "o3": 34.5, "so2": 3.0,
     "outdoor_activities": ["Đi biển", "Thể thao", "Tắm biển", "Du lịch"], "outdoor_score": 97, "best_time": "06:00 - 09:00, 15:30 - 18:30", "outdoor_advice": "Thiên đường nghỉ dưỡng ngoài trời hôm nay! Tắm biển Trần Phú, lặn ngắm san hô vịnh Nha Trang."},

    {"id": "VN_DL", "name": "Đắk Lắk", "province": "Đắk Lắk", "region": "Miền Trung", "type": "Tỉnh", "lat": 12.6667, "lon": 108.0500,
     "condition": "sunny", "weather_text": "Nắng ấm Buôn Ma Thuột, hương cà phê", "temp": 25.2, "feels_like": 25.5, "humidity": 64, "wind_speed": 3.2, "wind_dir": "Đông Bắc",
     "rain_prob": 5, "rain_mm": 0.0, "uv": 6.8, "pressure": 1013, "visibility": 12.5, "pm25": 14.0, "pm10": 23.5, "no2": 8.5, "co": 0.32, "o3": 35.0, "so2": 2.5,
     "outdoor_activities": ["Du lịch", "Cà phê", "Picnic"], "outdoor_score": 94, "best_time": "07:30 - 11:00, 14:30 - 17:30", "outdoor_advice": "Khí hậu mát mẻ, cà phê ngoài trời tại Buôn Ma Thuột và khám phá thác Dray Nur."},

    {"id": "VN_LD", "name": "Lâm Đồng", "province": "Lâm Đồng", "region": "Miền Trung", "type": "Tỉnh", "lat": 11.9404, "lon": 108.4583,
     "condition": "partly_cloudy", "weather_text": "Đà Lạt se lạnh thông reo, nắng dịu", "temp": 17.0, "feels_like": 17.0, "humidity": 75, "wind_speed": 2.8, "wind_dir": "Đông Bắc",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 6.0, "pressure": 1016, "visibility": 11.0, "pm25": 10.2, "pm10": 17.0, "no2": 6.5, "co": 0.25, "o3": 38.0, "so2": 1.8,
     "outdoor_activities": ["Đi dạo", "Chụp ảnh", "Đạp xe", "Picnic", "Cà phê"], "outdoor_score": 98, "best_time": "07:30 - 11:30, 14:00 - 17:30", "outdoor_advice": "Điểm số ngoài trời cao nhất toàn quốc (98/100)! Rất lý tưởng dạo hồ Xuân Hương, săn mây đồi chè Cầu Đất."},

    {"id": "VN_DNA", "name": "Đồng Nai", "province": "Đồng Nai", "region": "Miền Nam", "type": "Tỉnh", "lat": 10.9574, "lon": 106.8427,
     "condition": "partly_cloudy", "weather_text": "Nắng ráo, gió nhẹ sông Đồng Nai", "temp": 31.0, "feels_like": 33.5, "humidity": 68, "wind_speed": 2.8, "wind_dir": "Đông Nam",
     "rain_prob": 20, "rain_mm": 0.0, "uv": 7.8, "pressure": 1010, "visibility": 10.0, "pm25": 30.2, "pm10": 49.5, "no2": 21.0, "co": 0.82, "o3": 25.0, "so2": 4.5,
     "outdoor_activities": ["Dã ngoại", "Picnic", "Chụp ảnh"], "outdoor_score": 81, "best_time": "07:00 - 09:30, 16:00 - 18:30", "outdoor_advice": "Dã ngoại rừng Nam Cát Tiên hoặc cắm trại hồ Trị An rất thích hợp."},

    {"id": "VN_TN_S", "name": "Tây Ninh", "province": "Tây Ninh", "region": "Miền Nam", "type": "Tỉnh", "lat": 11.3104, "lon": 106.0984,
     "condition": "sunny", "weather_text": "Nắng đỉnh núi Bà Đen, gió thoảng", "temp": 31.2, "feels_like": 33.0, "humidity": 65, "wind_speed": 3.0, "wind_dir": "Đông",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 8.0, "pressure": 1011, "visibility": 11.0, "pm25": 22.0, "pm10": 36.5, "no2": 13.5, "co": 0.55, "o3": 27.0, "so2": 3.5,
     "outdoor_activities": ["Leo núi", "Trekking", "Du lịch"], "outdoor_score": 86, "best_time": "06:00 - 09:00, 16:00 - 18:30", "outdoor_advice": "Săn mây đỉnh núi Bà Đen sáng sớm; buổi trưa cần nón rộng và kem chống nắng."},

    {"id": "VN_DT", "name": "Đồng Tháp", "province": "Đồng Tháp", "region": "Miền Nam", "type": "Tỉnh", "lat": 10.4578, "lon": 105.6334,
     "condition": "partly_cloudy", "weather_text": "Gió đồng sen Tháp Mười ngan ngát", "temp": 30.5, "feels_like": 32.8, "humidity": 71, "wind_speed": 2.7, "wind_dir": "Đông Nam",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 7.5, "pressure": 1011, "visibility": 10.5, "pm25": 19.5, "pm10": 33.0, "no2": 12.0, "co": 0.48, "o3": 28.0, "so2": 3.2,
     "outdoor_activities": ["Du lịch", "Tham quan", "Chụp ảnh"], "outdoor_score": 88, "best_time": "06:30 - 09:30, 15:30 - 18:00", "outdoor_advice": "Tham quan làng hoa Sa Đéc và vườn quốc gia Tràm Chim mùa chim về."},

    {"id": "VN_VL", "name": "Vĩnh Long", "province": "Vĩnh Long", "region": "Miền Nam", "type": "Tỉnh", "lat": 10.2537, "lon": 105.9722,
     "condition": "sunny", "weather_text": "Nắng ấm vườn trái cây cù lao An Bình", "temp": 30.0, "feels_like": 32.2, "humidity": 73, "wind_speed": 2.6, "wind_dir": "Nam",
     "rain_prob": 15, "rain_mm": 0.0, "uv": 7.4, "pressure": 1011, "visibility": 11.0, "pm25": 18.0, "pm10": 30.5, "no2": 11.5, "co": 0.45, "o3": 29.0, "so2": 3.0,
     "outdoor_activities": ["Du lịch", "Picnic", "Dã ngoại"], "outdoor_score": 89, "best_time": "07:00 - 10:00, 15:30 - 18:00", "outdoor_advice": "Du ngoạn sông nước miệt vườn cù lao An Bình, trải nghiệm ẩm thực miền Tây."},

    {"id": "VN_AG", "name": "An Giang", "province": "An Giang", "region": "Miền Nam", "type": "Tỉnh", "lat": 10.3833, "lon": 105.4167,
     "condition": "sunny", "weather_text": "Nắng rọi rừng tràm Trà Sư xanh ngắt", "temp": 30.8, "feels_like": 33.0, "humidity": 70, "wind_speed": 2.9, "wind_dir": "Đông Nam",
     "rain_prob": 10, "rain_mm": 0.0, "uv": 7.6, "pressure": 1011, "visibility": 11.5, "pm25": 17.5, "pm10": 29.0, "no2": 11.0, "co": 0.42, "o3": 30.0, "so2": 2.8,
     "outdoor_activities": ["Du lịch", "Chụp ảnh", "Tham quan"], "outdoor_score": 91, "best_time": "06:30 - 09:30, 15:30 - 18:00", "outdoor_advice": "Check-in rừng tràm Trà Sư tuyệt đẹp lúc sáng sớm, viếng miếu Bà Chúa Xứ."},

    {"id": "VN_CM", "name": "Cà Mau", "province": "Cà Mau", "region": "Miền Nam", "type": "Tỉnh", "lat": 9.1769, "lon": 105.1524,
     "condition": "partly_cloudy", "weather_text": "Gió biển Đất Mũi dạt dào, nắng nhẹ", "temp": 29.5, "feels_like": 31.8, "humidity": 76, "wind_speed": 3.8, "wind_dir": "Đông Nam",
     "rain_prob": 20, "rain_mm": 0.0, "uv": 7.0, "pressure": 1011, "visibility": 10.5, "pm25": 14.2, "pm10": 24.0, "no2": 9.5, "co": 0.38, "o3": 32.0, "so2": 2.5,
     "outdoor_activities": ["Du lịch", "Tham quan", "Chụp ảnh"], "outdoor_score": 90, "best_time": "07:00 - 10:00, 15:00 - 18:00", "outdoor_advice": "Thời tiết đất Mũi mát mẻ, lý tưởng để tham quan cột mốc tọa độ quốc gia GPS 0001."}
]
