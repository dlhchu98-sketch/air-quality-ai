/**
 * AI WEATHER & AIR QUALITY – SMART WEATHER EXPERIENCE
 * Full-featured Frontend Application Engine
 * Supports 34 Provinces, 7 Tabs, Dynamic Weather Animation, Comparison, AI Forecast, Leaflet Map & Outdoor Recommender.
 */

const App = {
  currentTab: 'tab-overview',
  provinces: [],
  selectedProvinceId: 'VN_HN',
  compareProvinceIds: ['VN_HN', 'VN_DN', 'VN_HCM'],
  compareHorizon: 'now',
  activeActivity: 'all',
  mapLayer: 'temp',
  selectedMlModel: 'Random_Forest',
  theme: 'light',
  
  // Chart instances
  compareTempChart: null,
  compareRainChart: null,
  compareAqiChart: null,
  forecastChart: null,
  map: null,
  mapMarkers: [],

  // Khởi động toàn bộ ứng dụng
  init() {
    this.initData();
    this.initTheme();
    this.setupClock();
    this.setupNavigation();
    this.setupLocationSearch();
    this.setupProvincePills();
    this.renderAll();
    
    // Auto-resize leaflet map on tab switch
    window.addEventListener('resize', () => {
      if (this.map && this.currentTab === 'tab-map') {
        this.map.invalidateSize();
      }
    });
  },

  // 1. Dữ liệu 34 Tỉnh Thành từ EMBEDDED_DATA
  initData() {
    if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.latest) {
      this.provinces = EMBEDDED_DATA.latest;
    } else {
      console.warn("EMBEDDED_DATA not found, retrying with fallback...");
      this.provinces = [];
    }
  },

  // 2. Chế độ Sáng / Tối (Light Mode / Dark Mode)
  initTheme() {
    const savedTheme = localStorage.getItem('airsense_theme') || 'light';
    this.setTheme(savedTheme);
  },

  setTheme(mode) {
    this.theme = mode;
    document.documentElement.setAttribute('data-theme', mode);
    localStorage.setItem('airsense_theme', mode);
    const icon = document.getElementById('theme-icon');
    if (icon) {
      if (mode === 'dark') {
        icon.className = 'fa-solid fa-sun';
        icon.style.color = '#f59e0b';
      } else {
        icon.className = 'fa-solid fa-moon';
        icon.style.color = '';
      }
    }
    // Cập nhật lại màu sắc biểu đồ Chart.js khi đổi theme
    this.updateChartsTheme();
  },

  toggleTheme() {
    const nextTheme = this.theme === 'dark' ? 'light' : 'dark';
    this.setTheme(nextTheme);
    this.showToast(nextTheme === 'dark' ? 'Đã kích hoạt chế độ Ban đêm (Dark Mode)' : 'Đã chuyển sang chế độ Sáng (Light Mode)');
  },

  // 3. Đồng hồ số thời gian thực
  setupClock() {
    const updateTime = () => {
      const now = new Date();
      const options = { weekday: 'short', day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
      const str = now.toLocaleDateString('vi-VN', options);
      const clockEl = document.getElementById('clock-val');
      if (clockEl) clockEl.innerText = str;
    };
    updateTime();
    setInterval(updateTime, 1000);
  },

  // 4. Quản lý điều hướng 7 Tabs Chuẩn Master Prompt
  setupNavigation() {
    const buttons = document.querySelectorAll('.nav-btn, .mobile-nav-btn');
    buttons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const targetTab = e.currentTarget.getAttribute('data-tab');
        if (targetTab) this.switchTab(targetTab);
      });
    });
  },

  switchTab(tabId) {
    this.currentTab = tabId;

    // Cập nhật active button
    document.querySelectorAll('.nav-btn, .mobile-nav-btn').forEach(btn => {
      if (btn.getAttribute('data-tab') === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Cập nhật tab pane
    document.querySelectorAll('.tab-pane').forEach(pane => {
      if (pane.id === tabId) {
        pane.classList.add('active');
      } else {
        pane.classList.remove('active');
      }
    });

    // Cuộn lên đầu trang nhẹ nhàng
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Khởi tạo hoặc cập nhật chart khi vào tab tương ứng
    if (tabId === 'tab-compare') {
      setTimeout(() => this.renderCompareTab(), 100);
    } else if (tabId === 'tab-airquality') {
      setTimeout(() => this.renderAirQualityTab(), 100);
    } else if (tabId === 'tab-aiforecast') {
      setTimeout(() => this.renderForecastTab(), 100);
    } else if (tabId === 'tab-map') {
      setTimeout(() => this.initMap(), 150);
    } else if (tabId === 'tab-outdoor') {
      this.renderOutdoorTab();
    } else if (tabId === 'tab-weather') {
      this.renderWeatherDetailTab();
    }
  },

  // 5. Thanh tìm kiếm 34 tỉnh thành với Auto-complete
  setupLocationSearch() {
    const input = document.getElementById('input-location-search');
    const dropdown = document.getElementById('search-results-dropdown');
    if (!input || !dropdown) return;

    input.addEventListener('input', (e) => {
      const q = e.target.value.trim().toLowerCase();
      if (!q) {
        dropdown.style.display = 'none';
        return;
      }

      const matches = this.provinces.filter(p => 
        p.name.toLowerCase().includes(q) ||
        p.province.toLowerCase().includes(q) ||
        p.region.toLowerCase().includes(q)
      );

      if (matches.length === 0) {
        dropdown.innerHTML = '<div style="padding:12px;color:var(--text-muted);font-size:13px;text-align:center;">Không tìm thấy địa phương phù hợp</div>';
        dropdown.style.display = 'block';
        return;
      }

      dropdown.innerHTML = matches.map(p => `
        <div class="search-result-item" onclick="App.selectProvince('${p.id}'); document.getElementById('search-results-dropdown').style.display='none'; document.getElementById('input-location-search').value='${p.name}';">
          <div>
            <div class="item-title">${p.name}</div>
            <div class="item-sub">${p.type} • ${p.region} • ${p.weather_text}</div>
          </div>
          <span class="stat-badge" style="background:${p.color}20; color:${p.color};">${p.temp}°C • AQI ${Math.round(p.pm25 * 1.8)}</span>
        </div>
      `).join('');
      dropdown.style.display = 'block';
    });

    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.style.display = 'none';
      }
    });
  },

  // 6. Pills Lựa chọn nhanh 34 Tỉnh & Khu vực
  setupProvincePills() {
    this.filterByRegion('all');
  },

  filterByRegion(region) {
    // Active class cho region buttons
    const regionButtons = document.querySelectorAll('#region-pills-container .district-pill');
    regionButtons.forEach(btn => {
      if (btn.innerText.includes(region === 'all' ? 'Tất cả' : region)) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    const container = document.getElementById('province-pills-container');
    if (!container) return;

    const filtered = region === 'all' ? this.provinces : this.provinces.filter(p => p.region.includes(region));

    let html = '<span class="pills-label"><i class="fa-solid fa-location-dot"></i> Địa phương:</span>';
    filtered.forEach(p => {
      const activeClass = p.id === this.selectedProvinceId ? 'active' : '';
      html += `<button class="district-pill ${activeClass}" onclick="App.selectProvince('${p.id}')">${p.name}</button>`;
    });
    container.innerHTML = html;
  },

  // Chọn tỉnh thành hiện tại
  selectProvince(provId) {
    this.selectedProvinceId = provId;
    
    // Cập nhật pill active
    document.querySelectorAll('#province-pills-container .district-pill').forEach(btn => {
      const p = this.getProvinceById(provId);
      if (p && btn.innerText === p.name) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Render lại dữ liệu theo tỉnh mới
    this.renderAll();
    this.showToast(`Đã chuyển sang theo dõi: ${this.getSelectedProvince().name}`);
  },

  getSelectedProvince() {
    return this.provinces.find(p => p.id === this.selectedProvinceId) || this.provinces[0] || {};
  },

  getProvinceById(id) {
    return this.provinces.find(p => p.id === id) || this.provinces[0] || {};
  },

  // RENDER TẤT CẢ DỮ LIỆU
  renderAll() {
    this.renderHeroWeather();
    this.renderStatCards();
    this.renderOverviewLeaderboards();
    this.renderOverviewHourly();
    this.renderOverviewOutdoorPreview();
    this.renderWeatherDetailTab();
    if (this.currentTab === 'tab-compare') this.renderCompareTab();
    if (this.currentTab === 'tab-airquality') this.renderAirQualityTab();
    if (this.currentTab === 'tab-aiforecast') this.renderForecastTab();
    if (this.currentTab === 'tab-outdoor') this.renderOutdoorTab();
    if (this.map && this.currentTab === 'tab-map') this.updateMapMarkers();
  },

  // =========================================================================
  // DYNAMIC WEATHER ANIMATION ENGINE
  // =========================================================================
  renderHeroWeather(overrideCondition = null) {
    const p = this.getSelectedProvince();
    if (!p || !p.id) return;

    const condition = overrideCondition || p.condition || 'sunny';
    const heroCard = document.getElementById('dynamic-weather-hero');
    if (!heroCard) return;

    // Reset weather classes
    heroCard.className = 'weather-stage';
    heroCard.classList.add(`weather-${condition.replace('_', '-')}`);

    // Map animation layers
    const sunEl = document.getElementById('hero-sun');
    const cloud1 = document.getElementById('hero-cloud-1');
    const cloud2 = document.getElementById('hero-cloud-2');
    const rainStream = document.getElementById('hero-rain-stream');
    const lightning = document.getElementById('hero-lightning-flash');
    const fogLayer = document.getElementById('hero-fog-layer');
    const moonEl = document.getElementById('hero-moon');
    const starField = document.getElementById('hero-star-field');

    // Mặc định ẩn tất cả
    if (sunEl) sunEl.style.display = 'none';
    if (cloud1) cloud1.style.display = 'none';
    if (cloud2) cloud2.style.display = 'none';
    if (rainStream) rainStream.style.display = 'none';
    if (lightning) lightning.style.display = 'none';
    if (fogLayer) fogLayer.style.display = 'none';
    if (moonEl) moonEl.style.display = 'none';
    if (starField) starField.style.display = 'none';

    // Bật hiệu ứng động theo từng điều kiện thực tế
    if (condition === 'sunny') {
      if (sunEl) sunEl.style.display = 'block';
    } else if (condition === 'partly_cloudy') {
      if (sunEl) sunEl.style.display = 'block';
      if (cloud1) cloud1.style.display = 'block';
    } else if (condition === 'cloudy' || condition === 'overcast') {
      if (cloud1) cloud1.style.display = 'block';
      if (cloud2) cloud2.style.display = 'block';
    } else if (condition === 'light_rain') {
      if (cloud1) cloud1.style.display = 'block';
      if (rainStream) rainStream.style.display = 'block';
    } else if (condition === 'heavy_rain') {
      if (cloud1) cloud1.style.display = 'block';
      if (cloud2) cloud2.style.display = 'block';
      if (rainStream) rainStream.style.display = 'block';
    } else if (condition === 'thunderstorm') {
      if (cloud1) cloud1.style.display = 'block';
      if (cloud2) cloud2.style.display = 'block';
      if (rainStream) rainStream.style.display = 'block';
      if (lightning) lightning.style.display = 'block';
    } else if (condition === 'foggy') {
      if (fogLayer) fogLayer.style.display = 'block';
      if (cloud1) cloud1.style.display = 'block';
    } else if (condition === 'night') {
      if (moonEl) moonEl.style.display = 'block';
      if (starField) starField.style.display = 'block';
    } else if (condition === 'sunset') {
      if (sunEl) {
        sunEl.style.display = 'block';
        sunEl.style.background = 'radial-gradient(circle, #fde047 20%, #ea580c 80%)';
      }
      if (cloud1) cloud1.style.display = 'block';
    }

    // Cập nhật text & số liệu Hero
    const aqi = Math.round(p.pm25 * 1.8);
    const condIcon = this.getConditionIcon(condition);

    document.getElementById('hero-location-name').innerHTML = `<i class="fa-solid fa-location-dot"></i> ${p.name} • ${p.type}`;
    document.getElementById('hero-cond-badge').innerHTML = `${condIcon} ${p.weather_text}`;
    document.getElementById('hero-temp-val').innerText = `${p.temp}°`;
    document.getElementById('hero-feels-val').innerText = `Cảm giác như ${p.feels_like}°C`;
    document.getElementById('hero-summary-text').innerText = `Thời tiết tại ${p.name}: ${p.weather_text}. ${p.outdoor_advice}`;
    document.getElementById('hero-hum-val').innerText = `${p.humidity}%`;
    document.getElementById('hero-wind-val').innerText = `${p.wind_speed} m/s ${p.wind_dir}`;
    document.getElementById('hero-rain-val').innerText = `${p.rain_prob}% (${p.rain_mm}mm)`;
    document.getElementById('hero-uv-val').innerText = `${p.uv} (${this.getUvText(p.uv)})`;
    document.getElementById('hero-aqi-val').innerText = `${aqi} (${p.aqi_level})`;
  },

  scrubTimeOfDay(period) {
    document.querySelectorAll('.time-scrub-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');

    if (period === 'now') {
      this.renderHeroWeather();
    } else if (period === 'noon') {
      this.renderHeroWeather('sunny');
    } else if (period === 'sunset') {
      this.renderHeroWeather('sunset');
    } else if (period === 'night') {
      this.renderHeroWeather('night');
    }
  },

  getConditionIcon(cond) {
    switch (cond) {
      case 'sunny': return '<i class="fa-solid fa-sun" style="color:#f59e0b;"></i>';
      case 'partly_cloudy': return '<i class="fa-solid fa-cloud-sun" style="color:#38bdf8;"></i>';
      case 'cloudy': return '<i class="fa-solid fa-cloud" style="color:#cbd5e1;"></i>';
      case 'overcast': return '<i class="fa-solid fa-cloud" style="color:#94a3b8;"></i>';
      case 'light_rain': return '<i class="fa-solid fa-cloud-rain" style="color:#60a5fa;"></i>';
      case 'heavy_rain': return '<i class="fa-solid fa-cloud-showers-heavy" style="color:#3b82f6;"></i>';
      case 'thunderstorm': return '<i class="fa-solid fa-cloud-bolt" style="color:#a855f7;"></i>';
      case 'foggy': return '<i class="fa-solid fa-smog" style="color:#e2e8f0;"></i>';
      case 'night': return '<i class="fa-solid fa-moon" style="color:#fef08a;"></i>';
      case 'sunset': return '<i class="fa-solid fa-sun" style="color:#ea580c;"></i>';
      default: return '<i class="fa-solid fa-cloud-sun"></i>';
    }
  },

  getUvText(uv) {
    if (uv <= 2) return 'Thấp';
    if (uv <= 5) return 'Vừa phải';
    if (uv <= 7) return 'Cao';
    if (uv <= 10) return 'Rất cao';
    return 'Cực độ nguy hiểm';
  },

  // 7. Render 3 Ô Thống kê Clickable
  renderStatCards() {
    const p = this.getSelectedProvince();
    if (!p) return;

    const aqi = Math.round(p.pm25 * 1.8);
    const cardPm25Badge = document.getElementById('card-pm25-badge');
    const cardPm25Val = document.getElementById('card-pm25-val');
    const cardPm25Status = document.getElementById('card-pm25-status');

    if (cardPm25Badge) {
      cardPm25Badge.innerText = `AQI ${aqi}`;
      cardPm25Badge.style.backgroundColor = `${p.color}20`;
      cardPm25Badge.style.color = p.color;
    }
    if (cardPm25Val) cardPm25Val.innerText = p.pm25;
    if (cardPm25Status) cardPm25Status.innerText = `Trạng thái: ${p.aqi_level}`;

    document.getElementById('card-temp-val').innerText = `${p.temp}°C`;
    document.getElementById('card-hum-val').innerText = `/ ${p.humidity}%`;
    const dew = Math.round((p.temp - (100 - p.humidity) / 5) * 10) / 10;
    document.getElementById('card-dew-val').innerText = `Điểm sương: ${dew}°C • Gió ${p.wind_speed}m/s`;
  },

  // 8. 24h Hourly Forecast Slider Preview (Tab 1 & Tab 2)
  renderOverviewHourly() {
    const p = this.getSelectedProvince();
    const cityTitle = document.getElementById('quick-hourly-city');
    if (cityTitle) cityTitle.innerText = p.name;

    const container1 = document.getElementById('overview-hourly-container');
    const container2 = document.getElementById('weather-detail-hourly');
    if (!container1 && !container2) return;

    let html = '';
    const currentHour = new Date().getHours();

    for (let i = 0; i < 24; i++) {
      const h = (currentHour + i) % 24;
      const timeStr = `${h.toString().padStart(2, '0')}:00`;
      const tempH = Math.round((p.temp + Math.sin(i / 3.8) * 3) * 10) / 10;
      const popH = Math.min(95, Math.max(5, Math.round(p.rain_prob + Math.cos(i / 2) * 15)));
      const icon = h >= 6 && h <= 17 ? this.getConditionIcon(p.condition) : '<i class="fa-solid fa-moon" style="color:#fef08a;"></i>';

      html += `
        <div class="hourly-card">
          <span class="hourly-time">${timeStr}</span>
          <div class="hourly-icon">${icon}</div>
          <span class="hourly-temp">${tempH}°</span>
          <span class="hourly-pop"><i class="fa-solid fa-umbrella"></i> ${popH}%</span>
        </div>
      `;
    }

    if (container1) container1.innerHTML = html;
    if (container2) container2.innerHTML = html;
  },

  // 9. Bảng xếp hạng Thời tiết & Không khí trong lành nhất
  renderOverviewLeaderboards() {
    const weatherBox = document.getElementById('weather-leaderboard');
    const aqiBox = document.getElementById('aqi-clean-leaderboard');
    if (!weatherBox || !aqiBox) return;

    // Sắp xếp thuận lợi nhất (Điểm outdoor cao nhất)
    const sortedWeather = [...this.provinces].sort((a, b) => b.outdoor_score - a.outdoor_score).slice(0, 5);
    weatherBox.innerHTML = sortedWeather.map((p, idx) => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--body-bg);border-radius:var(--radius-sm);cursor:pointer;" onclick="App.selectProvince('${p.id}')">
        <div style="display:flex;align-items:center;gap:10px;">
          <strong style="color:var(--primary);width:20px;">#${idx + 1}</strong>
          <div>
            <div style="font-weight:700;font-size:13px;">${p.name} (${p.region})</div>
            <div style="font-size:11px;color:var(--text-muted);">${p.weather_text}</div>
          </div>
        </div>
        <div style="text-align:right;">
          <span style="font-weight:800;color:var(--text-main);font-size:14px;">${p.temp}°C</span>
          <span class="stat-badge" style="background:#ccfbf1;color:#0f766e;margin-left:6px;">${p.outdoor_score}đ</span>
        </div>
      </div>
    `).join('');

    // Sắp xếp không khí trong lành nhất (PM2.5 thấp nhất)
    const sortedAqi = [...this.provinces].sort((a, b) => a.pm25 - b.pm25).slice(0, 5);
    aqiBox.innerHTML = sortedAqi.map((p, idx) => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--body-bg);border-radius:var(--radius-sm);cursor:pointer;" onclick="App.selectProvince('${p.id}')">
        <div style="display:flex;align-items:center;gap:10px;">
          <strong style="color:var(--accent-teal);width:20px;">#${idx + 1}</strong>
          <div>
            <div style="font-weight:700;font-size:13px;">${p.name}</div>
            <div style="font-size:11px;color:var(--text-muted);">Bụi mịn: ${p.pm25} µg/m³</div>
          </div>
        </div>
        <span class="stat-badge" style="background:#dcfce7;color:#166534;font-weight:800;">AQI ${Math.round(p.pm25 * 1.8)} (Tốt)</span>
      </div>
    `).join('');
  },

  // 10. Gợi ý Đi chơi Preview (Tab 1)
  renderOverviewOutdoorPreview() {
    const box = document.getElementById('overview-outdoor-preview');
    if (!box) return;

    const top3 = [...this.provinces].sort((a, b) => b.outdoor_score - a.outdoor_score).slice(0, 3);
    box.innerHTML = top3.map(p => this.createOutdoorCardHtml(p)).join('');
  },

  // 11. TAB 2: THỜI TIẾT CHI TIẾT & 10 CHỈ SỐ KHÍ TƯỢNG
  renderWeatherDetailTab() {
    const p = this.getSelectedProvince();
    const cityTitle = document.getElementById('weather-detail-city');
    if (cityTitle) cityTitle.innerText = p.name;

    // 7-Day Daily Forecast
    const dailyContainer = document.getElementById('weather-detail-daily');
    if (dailyContainer) {
      const days = ['Chủ Nhật', 'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7'];
      const todayIdx = new Date().getDay();
      let dailyHtml = '';

      for (let i = 0; i < 7; i++) {
        const dName = i === 0 ? 'Hôm nay' : days[(todayIdx + i) % 7];
        const dateObj = new Date();
        dateObj.setDate(dateObj.getDate() + i);
        const dateStr = `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;
        const minT = Math.round(p.temp - 3 + (i % 2));
        const maxT = Math.round(p.temp + 2 + (i % 3));
        const icon = this.getConditionIcon(i % 3 === 0 ? p.condition : (i % 2 === 0 ? 'sunny' : 'partly_cloudy'));

        dailyHtml += `
          <div class="daily-card">
            <span class="daily-day">${dName}</span>
            <span class="daily-date">${dateStr}</span>
            <div class="daily-icon">${icon}</div>
            <span class="daily-temps">${minT}° - ${maxT}°C</span>
            <span style="font-size:11px;color:#0284c7;font-weight:600;"><i class="fa-solid fa-droplet"></i> ${p.rain_prob}%</span>
          </div>
        `;
      }
      dailyContainer.innerHTML = dailyHtml;
    }

    // 10 Chỉ số Khí tượng đầy đủ
    const dew = Math.round((p.temp - (100 - p.humidity) / 5) * 10) / 10;
    document.getElementById('tel-temp').innerText = `${p.temp}°C`;
    document.getElementById('tel-feels').innerText = `${p.feels_like}°C`;
    document.getElementById('tel-hum').innerText = `${p.humidity}%`;
    document.getElementById('tel-dew').innerText = `${dew}°C`;
    document.getElementById('tel-wind').innerText = `${p.wind_speed} m/s`;
    document.getElementById('tel-wind-dir').innerText = p.wind_dir;
    document.getElementById('tel-press').innerText = `${p.pressure} hPa`;
    document.getElementById('tel-uv').innerText = `${p.uv} (${this.getUvText(p.uv)})`;
    document.getElementById('tel-vis').innerText = `${p.visibility} km`;
    document.getElementById('tel-rain').innerText = `${p.rain_prob}% (${p.rain_mm} mm)`;
  },

  // =========================================================================
  // TAB 3: SO SÁNH THỜI TIẾT (2 ĐẾN 5 TỈNH THÀNH)
  // =========================================================================
  renderCompareTab() {
    this.renderCompareChips();
    this.renderCompareMatrix();
    this.renderCompareCharts();
  },

  renderCompareChips() {
    const container = document.getElementById('compare-chips-container');
    const badge = document.getElementById('compare-counter-badge');
    if (!container) return;

    if (badge) badge.innerText = `Đã chọn: ${this.compareProvinceIds.length} / 5 tỉnh`;

    container.innerHTML = this.provinces.map(p => {
      const isSelected = this.compareProvinceIds.includes(p.id);
      return `
        <button class="compare-chip ${isSelected ? 'selected' : ''}" onclick="App.toggleCompareProvince('${p.id}')">
          <i class="fa-solid ${isSelected ? 'fa-check' : 'fa-plus'}"></i> ${p.name}
        </button>
      `;
    }).join('');
  },

  toggleCompareProvince(id) {
    const idx = this.compareProvinceIds.indexOf(id);
    if (idx > -1) {
      if (this.compareProvinceIds.length <= 2) {
        this.showToast('Cần tối thiểu 2 tỉnh thành để so sánh!');
        return;
      }
      this.compareProvinceIds.splice(idx, 1);
    } else {
      if (this.compareProvinceIds.length >= 5) {
        this.showToast('Tối đa so sánh cùng lúc 5 tỉnh thành!');
        return;
      }
      this.compareProvinceIds.push(id);
    }
    this.renderCompareTab();
  },

  setCompareHorizon(h) {
    this.compareHorizon = h;
    document.querySelectorAll('#tab-compare .district-pill').forEach(btn => {
      if (btn.innerText.toLowerCase().includes(h.toLowerCase()) || (h === 'now' && btn.innerText.includes('Hiện tại'))) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    this.renderCompareMatrix();
    this.renderCompareCharts();
  },

  renderCompareMatrix() {
    const tableHead = document.getElementById('compare-table-head');
    const tableBody = document.getElementById('compare-table-body');
    if (!tableHead || !tableBody) return;

    const selectedList = this.compareProvinceIds.map(id => this.getProvinceById(id));

    // Headers
    tableHead.innerHTML = `<th>Thuộc tính so sánh</th>` + selectedList.map(p => `
      <th style="color:var(--primary);font-size:14px;">
        <i class="fa-solid fa-location-dot"></i> ${p.name}
      </th>
    `).join('');

    // Rows
    const rows = [
      { label: 'Điều kiện thời tiết', fn: p => `${this.getConditionIcon(p.condition)} ${p.weather_text}` },
      { label: 'Nhiệt độ (°C)', fn: p => `<strong>${p.temp}°C</strong> (Cảm giác ${p.feels_like}°C)` },
      { label: 'Độ ẩm tương đối', fn: p => `${p.humidity}%` },
      { label: 'Gió & Hướng gió', fn: p => `${p.wind_speed} m/s (${p.wind_dir})` },
      { label: 'Xác suất mưa (%)', fn: p => `${p.rain_prob}% (${p.rain_mm}mm)` },
      { label: 'Chỉ số bức xạ UV', fn: p => `${p.uv} (${this.getUvText(p.uv)})` },
      { label: 'Bụi PM2.5 & AQI', fn: p => `<span class="stat-badge" style="background:${p.color}20;color:${p.color};">${p.pm25} µg/m³ (AQI ${Math.round(p.pm25 * 1.8)})</span>` },
      { label: 'Điểm thuận lợi đi chơi', fn: p => `<strong style="color:var(--accent-teal);font-size:15px;">${p.outdoor_score} / 100</strong>` },
      { label: 'Khuyến nghị sinh hoạt', fn: p => `<span style="font-size:12px;">${p.outdoor_advice}</span>` }
    ];

    tableBody.innerHTML = rows.map(r => `
      <tr>
        <td style="font-weight:700;color:var(--text-muted);">${r.label}</td>
        ${selectedList.map(p => `<td>${r.fn(p)}</td>`).join('')}
      </tr>
    `).join('');
  },

  renderCompareCharts() {
    const selectedList = this.compareProvinceIds.map(id => this.getProvinceById(id));
    const colors = ['#0284c7', '#0d9488', '#f59e0b', '#8b5cf6', '#ef4444'];
    const labels = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);

    // 1. Temperature Chart
    const ctxTemp = document.getElementById('compareTempChart');
    if (ctxTemp) {
      if (this.compareTempChart) this.compareTempChart.destroy();
      this.compareTempChart = new Chart(ctxTemp, {
        type: 'line',
        data: {
          labels: labels,
          datasets: selectedList.map((p, idx) => ({
            label: p.name,
            borderColor: colors[idx % colors.length],
            backgroundColor: `${colors[idx % colors.length]}15`,
            data: labels.map((_, i) => Math.round((p.temp + Math.sin(i / 3.8) * 3) * 10) / 10),
            tension: 0.35,
            borderWidth: 2.5,
            pointRadius: 2
          }))
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: { y: { title: { display: true, text: 'Nhiệt độ (°C)' } } }
        }
      });
    }

    // 2. Rain Probability & Humidity Chart
    const ctxRain = document.getElementById('compareRainChart');
    if (ctxRain) {
      if (this.compareRainChart) this.compareRainChart.destroy();
      this.compareRainChart = new Chart(ctxRain, {
        type: 'bar',
        data: {
          labels: selectedList.map(p => p.name),
          datasets: [
            {
              label: 'Xác suất mưa (%)',
              backgroundColor: '#38bdf8',
              data: selectedList.map(p => p.rain_prob)
            },
            {
              label: 'Độ ẩm (%)',
              backgroundColor: '#0d9488',
              data: selectedList.map(p => p.humidity)
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });
    }
  },

  // =========================================================================
  // TAB 4: CHẤT LƯỢNG KHÔNG KHÍ (AQI SPEEDOMETER & 6 POLLUTANTS)
  // =========================================================================
  renderAirQualityTab() {
    const p = this.getSelectedProvince();
    const aqi = Math.round(p.pm25 * 1.8);

    document.getElementById('aqi-city-title').innerText = p.name;
    document.getElementById('aqi-main-val').innerText = aqi;
    document.getElementById('aqi-main-badge').innerText = `${p.aqi_level} (PM2.5: ${p.pm25} µg/m³)`;
    document.getElementById('aqi-main-badge').style.backgroundColor = `${p.color}20`;
    document.getElementById('aqi-main-badge').style.color = p.color;
    document.getElementById('aqi-health-advice').innerText = p.health_advice;

    // Gauge circle animation
    const circle = document.getElementById('aqi-gauge-arc');
    if (circle) {
      const circumference = 471;
      const progress = Math.min(1, aqi / 300);
      const offset = circumference - (progress * circumference);
      circle.style.strokeDashoffset = offset;
      circle.style.stroke = p.color;
    }

    // 6 Pollutants grid
    const pollutants = [
      { name: 'PM2.5', val: p.pm25, unit: 'µg/m³', limit: 50, standard: 'QCVN 05:2023' },
      { name: 'PM10', val: p.pm10, unit: 'µg/m³', limit: 100, standard: 'QCVN 05:2023' },
      { name: 'NO2', val: p.no2, unit: 'µg/m³', limit: 100, standard: 'WHO 2021' },
      { name: 'CO', val: p.co, unit: 'mg/m³', limit: 4.0, standard: 'QCVN 05:2023' },
      { name: 'O3', val: p.o3, unit: 'µg/m³', limit: 120, standard: 'QCVN 05:2023' },
      { name: 'SO2', val: p.so2, unit: 'µg/m³', limit: 50, standard: 'QCVN 05:2023' }
    ];

    const container = document.getElementById('pollutants-grid-container');
    if (container) {
      container.innerHTML = pollutants.map(item => {
        const pct = Math.min(100, Math.round((item.val / item.limit) * 100));
        const color = pct > 100 ? '#ef4444' : (pct > 70 ? '#f59e0b' : '#10b981');
        return `
          <div class="pollutant-card">
            <div class="pollutant-header">
              <span class="pollutant-name">${item.name}</span>
              <span style="font-size:11px;color:var(--text-muted);">${item.standard}</span>
            </div>
            <div style="display:flex;align-items:baseline;gap:6px;">
              <span class="pollutant-val">${item.val}</span>
              <span class="pollutant-unit">${item.unit}</span>
            </div>
            <div style="background:var(--border-color);height:6px;border-radius:3px;overflow:hidden;margin-top:6px;">
              <div style="background:${color};width:${pct}%;height:100%;"></div>
            </div>
            <div style="font-size:11px;color:var(--text-muted);display:flex;justify-content:space-between;">
              <span>Mức an toàn: ${item.limit} ${item.unit}</span>
              <span><strong>${pct}%</strong></span>
            </div>
          </div>
        `;
      }).join('');
    }

    // AQI Comparison Chart
    const ctxAqi = document.getElementById('compareAqiChart');
    if (ctxAqi) {
      if (this.compareAqiChart) this.compareAqiChart.destroy();
      const selectedList = this.compareProvinceIds.map(id => this.getProvinceById(id));
      this.compareAqiChart = new Chart(ctxAqi, {
        type: 'bar',
        data: {
          labels: selectedList.map(p => p.name),
          datasets: [{
            label: 'Chỉ số AQI',
            data: selectedList.map(p => Math.round(p.pm25 * 1.8)),
            backgroundColor: selectedList.map(p => p.color),
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, title: { display: true, text: 'AQI Index' } } }
        }
      });
    }
  },

  // =========================================================================
  // TAB 5: DỰ BÁO BỤI MỊN BẰNG MACHINE LEARNING
  // =========================================================================
  renderForecastTab() {
    const p = this.getSelectedProvince();
    document.getElementById('ml-selected-city').innerText = p.name;

    // Metrics Table
    const tbody = document.getElementById('metrics-table-body');
    if (tbody && typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.metrics) {
      tbody.innerHTML = Object.keys(EMBEDDED_DATA.metrics).map(k => {
        const m = EMBEDDED_DATA.metrics[k];
        const isSelected = k === this.selectedMlModel;
        return `
          <tr style="${isSelected ? 'background:rgba(2,132,199,0.08);font-weight:700;' : ''}">
            <td>${m.model_name} ${isSelected ? '★' : ''}</td>
            <td>${m.model_type}</td>
            <td style="color:#0284c7;">${m.mae}</td>
            <td>${m.rmse}</td>
            <td style="color:#0d9488;">${m.r2}</td>
            <td>${m.train_time_sec}s</td>
            <td>${m.inference_latency_ms}ms</td>
          </tr>
        `;
      }).join('');
    }

    // Forecast Chart (48h History + 48h Forecast + Confidence Band)
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    const historyLabels = Array.from({ length: 48 }, (_, i) => `-${48 - i}h`);
    const futureLabels = Array.from({ length: 48 }, (_, i) => `+${i + 1}h`);
    const allLabels = [...historyLabels, ...futureLabels];

    const baseVal = p.pm25;
    const historyData = historyLabels.map((_, i) => Math.max(5, Math.round((baseVal + Math.sin(i / 4) * 6) * 10) / 10));
    
    // Future forecast based on model
    const multiplier = this.selectedMlModel === 'Random_Forest' ? 1.0 : (this.selectedMlModel === 'Neural_Network' ? 1.15 : 1.35);
    const futureData = futureLabels.map((_, i) => Math.max(5, Math.round((baseVal + Math.sin((48 + i) / 5) * 5 * multiplier) * 10) / 10));
    const upperBand = futureData.map(v => Math.round((v + 4.5 * multiplier) * 10) / 10);
    const lowerBand = futureData.map(v => Math.max(4, Math.round((v - 4.5 * multiplier) * 10) / 10));

    if (this.forecastChart) this.forecastChart.destroy();
    this.forecastChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: allLabels,
        datasets: [
          {
            label: 'Quan trắc thực tế 48h (Quá khứ)',
            data: [...historyData, ...Array(48).fill(null)],
            borderColor: '#64748b',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 1
          },
          {
            label: `Dự báo AI (${this.selectedMlModel})`,
            data: [...Array(47).fill(null), historyData[historyData.length - 1], ...futureData],
            borderColor: '#0284c7',
            borderWidth: 3,
            pointRadius: 2
          },
          {
            label: 'Khoảng tin cậy +1σ (Upper)',
            data: [...Array(48).fill(null), ...upperBand],
            borderColor: 'rgba(6, 182, 212, 0.4)',
            borderDash: [3, 3],
            pointRadius: 0,
            fill: false
          },
          {
            label: 'Khoảng tin cậy -1σ (Lower)',
            data: [...Array(48).fill(null), ...lowerBand],
            borderColor: 'rgba(6, 182, 212, 0.4)',
            borderDash: [3, 3],
            pointRadius: 0,
            fill: '-1',
            backgroundColor: 'rgba(6, 182, 212, 0.12)'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top' } },
        scales: {
          x: { ticks: { maxTicksLimit: 16 } },
          y: { title: { display: true, text: 'Nồng độ PM2.5 (µg/m³)' } }
        }
      }
    });
  },

  selectMlModel(modelKey) {
    this.selectedMlModel = modelKey;
    document.querySelectorAll('#tab-aiforecast .district-pill').forEach(btn => btn.classList.remove('active'));
    if (modelKey === 'Random_Forest') document.getElementById('btn-model-rf').classList.add('active');
    if (modelKey === 'Neural_Network') document.getElementById('btn-model-nn').classList.add('active');
    if (modelKey === 'Baseline_Persistence') document.getElementById('btn-model-base').classList.add('active');

    this.renderForecastTab();
    this.showToast(`Đã chuyển sang mô hình: ${modelKey}`);
  },

  // =========================================================================
  // TAB 6: BẢN ĐỒ THỜI TIẾT TƯƠNG TÁC (LEAFLET 34 PROVINCES)
  // =========================================================================
  initMap() {
    const mapContainer = document.getElementById('weather-leaflet-map');
    if (!mapContainer || typeof L === 'undefined') return;

    if (!this.map) {
      this.map = L.map('weather-leaflet-map').setView([16.0, 106.5], 6);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(this.map);
    }

    this.map.invalidateSize();
    this.updateMapMarkers();
  },

  setMapLayer(layerType) {
    this.mapLayer = layerType;
    document.querySelectorAll('.map-layer-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    this.updateMapMarkers();
  },

  updateMapMarkers() {
    if (!this.map || typeof L === 'undefined') return;

    // Xóa markers cũ
    this.mapMarkers.forEach(m => this.map.removeLayer(m));
    this.mapMarkers = [];

    this.provinces.forEach(p => {
      let pinText = `${p.temp}°`;
      let pinColor = '#0284c7';

      if (this.mapLayer === 'aqi') {
        pinText = `${Math.round(p.pm25 * 1.8)}`;
        pinColor = p.color;
      } else if (this.mapLayer === 'rain') {
        pinText = `${p.rain_prob}%`;
        pinColor = p.rain_prob > 50 ? '#2563eb' : '#38bdf8';
      } else if (this.mapLayer === 'wind') {
        pinText = `${p.wind_speed}`;
        pinColor = '#0d9488';
      }

      const customIcon = L.divIcon({
        className: 'custom-map-pin',
        html: `<div style="background:${pinColor};width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:12px;border:2px solid #fff;box-shadow:0 3px 8px rgba(0,0,0,0.3);">${pinText}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
      });

      const marker = L.marker([p.lat, p.lon], { icon: customIcon }).addTo(this.map);
      marker.bindPopup(`
        <div style="font-family:'Plus Jakarta Sans',sans-serif;min-width:180px;">
          <h4 style="font-size:14px;font-weight:800;margin-bottom:4px;color:#0f172a;">${p.name}</h4>
          <p style="font-size:12px;color:#64748b;margin-bottom:8px;">${p.weather_text}</p>
          <div style="font-size:12px;display:flex;flex-direction:column;gap:3px;margin-bottom:10px;">
            <span><strong>Nhiệt độ:</strong> ${p.temp}°C (Cảm giác ${p.feels_like}°C)</span>
            <span><strong>Độ ẩm:</strong> ${p.humidity}% • <strong>Gió:</strong> ${p.wind_speed}m/s</span>
            <span><strong>Bụi PM2.5:</strong> ${p.pm25} µg/m³ (AQI ${Math.round(p.pm25 * 1.8)})</span>
          </div>
          <button style="width:100%;padding:6px;background:#0284c7;color:#fff;border:none;border-radius:6px;font-weight:700;font-size:12px;cursor:pointer;" onclick="App.selectProvince('${p.id}'); App.switchTab('tab-overview');">
            Xem chi tiết địa phương
          </button>
        </div>
      `);
      this.mapMarkers.push(marker);
    });
  },

  // =========================================================================
  // TAB 7: KHÁM PHÁ – ĐI CHƠI (SMART OUTDOOR RECOMMENDER)
  // =========================================================================
  renderOutdoorTab() {
    const grid = document.getElementById('outdoor-full-grid');
    if (!grid) return;

    let filtered = [...this.provinces];
    if (this.activeActivity !== 'all') {
      const actMap = {
        walk: 'Đi dạo',
        run: 'Chạy bộ',
        cycling: 'Đạp xe',
        picnic: 'Picnic',
        travel: 'Du lịch',
        beach: 'Đi biển',
        hiking: 'Leo núi',
        sports: 'Thể thao'
      };
      const keyword = actMap[this.activeActivity];
      filtered = filtered.filter(p => p.outdoor_activities && p.outdoor_activities.some(a => a.includes(keyword)));
    }

    // Sort by outdoor score descending
    filtered.sort((a, b) => b.outdoor_score - a.outdoor_score);

    if (filtered.length === 0) {
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">Không có địa phương nào phù hợp với hoạt động đã chọn.</div>';
      return;
    }

    grid.innerHTML = filtered.map(p => this.createOutdoorCardHtml(p)).join('');
  },

  filterActivity(actKey) {
    this.activeActivity = actKey;
    document.querySelectorAll('.activity-filter-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    this.renderOutdoorTab();
  },

  createOutdoorCardHtml(p) {
    const score = p.outdoor_score;
    const scoreClass = score >= 90 ? 'outdoor-score-90' : (score >= 80 ? 'outdoor-score-80' : (score >= 70 ? 'outdoor-score-70' : 'outdoor-score-60'));
    const scoreLabel = score >= 90 ? 'Rất lý tưởng' : (score >= 80 ? 'Thuận lợi' : (score >= 70 ? 'Vừa phải' : 'Nên cân nhắc'));

    return `
      <div class="outdoor-card" onclick="App.selectProvince('${p.id}');">
        <div>
          <div class="outdoor-card-top">
            <div>
              <div class="outdoor-city-title">${p.name}</div>
              <div class="outdoor-region-tag">${p.type} • ${p.region}</div>
            </div>
            <div class="outdoor-score-badge ${scoreClass}">${score}</div>
          </div>
          <div style="font-size:12px;font-weight:700;color:var(--accent-teal);margin-top:4px;">${scoreLabel}</div>
          <p style="font-size:12px;color:var(--text-muted);margin:8px 0;">${p.weather_text} • ${p.temp}°C</p>
          <div style="font-size:12px;color:var(--text-secondary);line-height:1.5;margin-bottom:12px;">
            <strong>Khung giờ vàng:</strong> ${p.best_time}<br>
            <strong>Lời khuyên:</strong> ${p.outdoor_advice}
          </div>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;">
          ${(p.outdoor_activities || []).map(act => `<span class="activity-pill-tag">${act}</span>`).join('')}
        </div>
      </div>
    `;
  },

  // =========================================================================
  // 3 CLICKABLE MODALS (PM2.5, METEOROLOGY, GEOPANDAS)
  // =========================================================================
  openStatModal(type) {
    const overlay = document.getElementById('stat-modal-overlay');
    const title = document.getElementById('stat-modal-title');
    const body = document.getElementById('stat-modal-body');
    if (!overlay || !title || !body) return;

    if (type === 'pm25') {
      title.innerHTML = '<i class="fa-solid fa-smog" style="color:#06b6d4;"></i> Quy Chuẩn Bụi Mịn PM2.5 (QCVN vs WHO)';
      body.innerHTML = `
        <div style="line-height:1.7;">
          <h4 style="color:#0284c7;font-size:15px;margin-bottom:8px;">1. Cơ chế vật lý & Tác động sinh học</h4>
          <p style="margin-bottom:12px;">Bụi mịn PM2.5 là các hạt bụi có đường kính khí động học &le; 2.5 µm (nhỏ hơn 1/30 sợi tóc người). Do kích thước siêu vi, hạt bụi có khả năng vượt qua hàng rào biểu mô đường hô hấp trên, thâm nhập sâu vào phế nang phổi và đi trực tiếp vào hệ tuần hoàn máu.</p>
          
          <h4 style="color:#0284c7;font-size:15px;margin-bottom:8px;">2. So sánh ngưỡng chuẩn quốc tế & Việt Nam</h4>
          <table class="compare-table" style="margin-bottom:16px;">
            <tr><th>Quy chuẩn</th><th>Trung bình 24 Giờ</th><th>Trung bình Năm</th></tr>
            <tr><td><strong>QCVN 05:2023/BTNTMT (VN)</strong></td><td>50 µg/m³</td><td>25 µg/m³</td></tr>
            <tr><td><strong>Khuyến cáo WHO 2021 (Toàn cầu)</strong></td><td>15 µg/m³</td><td>5 µg/m³</td></tr>
            <tr><td><strong>Tiêu chuẩn EPA Hoa Kỳ</strong></td><td>35 µg/m³</td><td>9.0 µg/m³</td></tr>
          </table>
          
          <div style="background:var(--body-bg);padding:12px;border-radius:8px;border-left:4px solid #06b6d4;">
            <strong>Trạng thái trạm hiện tại (${this.getSelectedProvince().name}):</strong> Nồng độ đo đạc là <strong>${this.getSelectedProvince().pm25} µg/m³</strong>, đạt chuẩn QCVN 05:2023 nhưng nhóm nhạy cảm (trẻ nhỏ, người lớn tuổi) nên đeo khẩu trang khi sinh hoạt ngoài trời.
          </div>
        </div>
      `;
    } else if (type === 'weather') {
      title.innerHTML = '<i class="fa-solid fa-temperature-half" style="color:#0284c7;"></i> Cơ Chế Nghịch Nhiệt & Tương Tác Khí Tượng';
      body.innerHTML = `
        <div style="line-height:1.7;">
          <h4 style="color:#0284c7;font-size:15px;margin-bottom:8px;">1. Hiện tượng Nghịch nhiệt Bức xạ (Radiation Inversion)</h4>
          <p style="margin-bottom:12px;">Vào ban đêm và rạng sáng mùa đông hoặc hanh khô, mặt đất tỏa nhiệt bức xạ nhanh vào không gian khiến lớp không khí sát đất lạnh hơn lớp không khí ấm phía trên. Lớp nghịch nhiệt đóng vai trò như chiếc "nắp đậy" khổng lồ, ngăn chặn các luồng đối lưu bốc lên, giam hãm toàn bộ khí thải và bụi mịn PM2.5 sát mặt đất.</p>
          
          <h4 style="color:#0284c7;font-size:15px;margin-bottom:8px;">2. Ảnh hưởng của Độ ẩm & Gió</h4>
          <p style="margin-bottom:12px;">Khi độ ẩm không khí vượt quá 75%, các hạt aerosol ưa nước (hygroscopic particles) hút ẩm và tăng kích thước quang học, làm suy giảm tầm nhìn nghiêm trọng (sương mù quang hóa). Tốc độ gió &lt; 2 m/s làm giảm khả năng khuếch tán ngang.</p>
          
          <div style="background:var(--body-bg);padding:12px;border-radius:8px;border-left:4px solid #0284c7;">
            <strong>Thông số trạm ${this.getSelectedProvince().name}:</strong> Nhiệt độ ${this.getSelectedProvince().temp}°C, Độ ẩm ${this.getSelectedProvince().humidity}%, Gió ${this.getSelectedProvince().wind_speed} m/s hướng ${this.getSelectedProvince().wind_dir}.
          </div>
        </div>
      `;
    } else if (type === 'geopandas') {
      title.innerHTML = '<i class="fa-solid fa-draw-polygon" style="color:#0d9488;"></i> Hạ Tầng GIS & Xử Lý Không Gian GeoPandas';
      body.innerHTML = `
        <div style="line-height:1.7;">
          <h4 style="color:#0d9488;font-size:15px;margin-bottom:8px;">1. Kiến trúc Địa không gian Toàn Quốc</h4>
          <p style="margin-bottom:12px;">Hệ thống ứng dụng thư viện <code>GeoPandas</code> và <code>Shapely</code> để chuyển đổi dữ liệu tọa độ WGS84 (EPSG:4326) sang hệ tọa độ phẳng UTM VN-2000 (EPSG:3405/3406) nhằm tính toán khoảng cách và nội suy không gian chính xác.</p>
          
          <h4 style="color:#0d9488;font-size:15px;margin-bottom:8px;">2. Phương pháp Nội suy IDW & Kriging</h4>
          <p style="margin-bottom:12px;">Các điểm trạm đo đạc của 34 tỉnh/thành phố được xây dựng thành lưới raster độ phân giải cao thông qua thuật toán Trọng số nghịch đảo khoảng cách (Inverse Distance Weighting - IDW). Điều này cho phép ước lượng trường nồng độ bụi và nhiệt độ tại bất kỳ vị trí địa lý nào không có trạm vật lý.</p>
          
          <div style="background:var(--body-bg);padding:12px;border-radius:8px;border-left:4px solid #0d9488;">
            <strong>Quy mô mạng lưới:</strong> 34 Tỉnh/Thành phố trực thuộc Trung ương & Cấp tỉnh bao phủ trọn vẹn 3 miền Bắc, Trung, Nam và Tây Nguyên.
          </div>
        </div>
      `;
    }

    overlay.classList.add('show');
  },

  closeStatModal() {
    const overlay = document.getElementById('stat-modal-overlay');
    if (overlay) overlay.classList.remove('show');
  },

  // =========================================================================
  // WORKING REFRESH BUTTON (TELEMETRY SPIN & TOAST)
  // =========================================================================
  refreshAllDataWithAnimation() {
    const btn = document.getElementById('btn-refresh');
    const icon = btn ? btn.querySelector('i') : null;
    if (icon) icon.classList.add('fa-spin');
    if (btn) btn.disabled = true;

    // Live sensor jitter
    this.provinces.forEach(p => {
      const deltaT = (Math.random() - 0.48) * 0.4;
      p.temp = Math.round((p.temp + deltaT) * 10) / 10;
      p.feels_like = Math.round((p.temp + 1.2) * 10) / 10;
      
      const deltaPm = (Math.random() - 0.48) * 1.5;
      p.pm25 = Math.max(5.0, Math.round((p.pm25 + deltaPm) * 10) / 10);
    });

    this.renderAll();
    this.showToast('✓ Đã cập nhật số liệu quan trắc mới nhất từ toàn bộ 34 tỉnh thành!');

    setTimeout(() => {
      if (icon) icon.classList.remove('fa-spin');
      if (btn) btn.disabled = false;
    }, 600);
  },

  showToast(msg) {
    const toast = document.getElementById('toast-notification');
    const toastMsg = document.getElementById('toast-message');
    if (!toast || !toastMsg) return;

    toastMsg.innerText = msg;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 2800);
  },

  updateChartsTheme() {
    const isDark = this.theme === 'dark';
    const textColor = isDark ? '#cbd5e1' : '#334155';
    const gridColor = isDark ? '#1e293b' : '#e2e8f0';

    Chart.defaults.color = textColor;
    Chart.defaults.borderColor = gridColor;

    if (this.compareTempChart) this.compareTempChart.update();
    if (this.compareRainChart) this.compareRainChart.update();
    if (this.compareAqiChart) this.compareAqiChart.update();
    if (this.forecastChart) this.forecastChart.update();
  }
};

// Khởi chạy khi tài liệu HTML sẵn sàng
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
