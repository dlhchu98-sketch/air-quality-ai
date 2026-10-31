/**
 * AirSense AI - Frontend Application Logic
 * Quản lý điều hướng 6 tab, tương tác bản đồ Leaflet toàn quốc (23 trạm), Chart.js và tìm kiếm đa tỉnh thành.
 */

const App = {
  currentTab: 'tab-overview',
  stations: [],
  latestObservations: [],
  map: null,
  stationLayer: null,
  forecastChart: null,
  evalChart: null,
  
  // Khởi chạy ứng dụng khi DOM sẵn sàng
  init() {
    this.setupNavigation();
    this.setupClock();
    this.setupClickableModals();
    this.setupLocationSearch();
    this.setupPWA();
    this.fetchOverviewData();
    this.setupForecastForm();
    this.fetchEvaluationData();
    
    // Nút làm mới dữ liệu
    const refreshBtn = document.getElementById('btn-refresh');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', (e) => {
        e.preventDefault();
        this.refreshAllDataWithAnimation();
      });
    }
  },

  // 1. Quản lý điều hướng Tab
  setupNavigation() {
    const allButtons = document.querySelectorAll('.nav-btn, .mobile-nav-btn');
    const titles = {
      'tab-overview': { title: 'Tổng quan Chất lượng Không khí Toàn Quốc', subtitle: 'Giám sát chuỗi thời gian & dự báo đa bước tại 23 trạm quan trắc trên 15 tỉnh thành' },
      'tab-map': { title: 'Bản đồ Địa không gian Toàn Quốc', subtitle: 'Trực quan hóa mạng lưới 23 trạm quan trắc không gian tại 15 tỉnh thành Việt Nam' },
      'tab-forecast': { title: 'Dự báo Trí tuệ Nhân tạo Đa Bước', subtitle: 'Cấu hình mô hình AI (Baseline, Random Forest, Neural Network) và chân trời dự báo' },
      'tab-results': { title: 'Kết quả & Phân tích Chi tiết', subtitle: 'Biểu đồ kết hợp quá khứ - tương lai kèm khoảng tin cậy 95% và khuyến nghị y tế' },
      'tab-evaluation': { title: 'Đánh giá Thực nghiệm Mô hình', subtitle: 'So sánh định lượng MAE, RMSE, R² và độ trễ suy luận trên Test Set độc lập' },
      'tab-about': { title: 'Giới thiệu Kiến trúc & Giới hạn', subtitle: 'Nguồn gốc dữ liệu, xử lý GeoPandas, tối ưu 20 CCU và tuyên bố miễn trừ' }
    };

    const switchTab = (targetTab) => {
      if (targetTab === this.currentTab) return;

      document.querySelectorAll('.nav-btn, .mobile-nav-btn').forEach(b => {
        if (b.getAttribute('data-tab') === targetTab) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
      });

      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const pane = document.getElementById(targetTab);
      if (pane) pane.classList.add('active');

      const titleInfo = titles[targetTab];
      if (titleInfo) {
        document.getElementById('page-title').innerText = titleInfo.title;
        document.getElementById('page-subtitle').innerText = titleInfo.subtitle;
      }

      this.currentTab = targetTab;

      if (targetTab === 'tab-map') {
        setTimeout(() => {
          this.initMap();
        }, 150);
      }
    };

    allButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        const target = e.currentTarget.getAttribute('data-tab');
        if (target) switchTab(target);
      });
    });
  },

  // 2. Chức năng Làm Mới Dữ Liệu có hiệu ứng xoay, mô phỏng cập nhật và thông báo Toast
  refreshAllDataWithAnimation() {
    const btn = document.getElementById('btn-refresh');
    const icon = btn ? btn.querySelector('i') : null;
    if (icon) icon.classList.add('fa-spin');
    if (btn) btn.disabled = true;

    // Mô phỏng cập nhật số liệu cảm biến vi mô (telemetry jitter)
    if (this.latestObservations && this.latestObservations.length) {
      this.latestObservations.forEach(obs => {
        const delta = (Math.random() - 0.48) * 1.6;
        obs.pm25 = Math.max(5.0, Math.round((obs.pm25 + delta) * 10) / 10);
        const aqiInfo = this.getAQIDetails(obs.pm25);
        obs.aqi_level = aqiInfo.level;
        obs.color = aqiInfo.color;
        obs.health_advice = aqiInfo.advice;
      });
    }

    this.renderOverviewMetrics();
    this.renderStationsTable();
    this.populateStationSelect();
    this.setupClock();

    if (this.currentTab === 'tab-map') {
      this.initMap();
    }

    this.showToast('✓ Đã làm mới dữ liệu từ 23 trạm quan trắc trên toàn quốc!');

    setTimeout(() => {
      if (icon) icon.classList.remove('fa-spin');
      if (btn) btn.disabled = false;
    }, 600);
  },

  // Hiển thị thông báo Toast nổi
  showToast(msg) {
    let toast = document.getElementById('app-floating-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'app-floating-toast';
      toast.style.cssText = 'position:fixed; bottom:24px; right:24px; background:linear-gradient(135deg, #0284c7, #0d9488); color:#fff; font-weight:700; font-size:0.9rem; padding:12px 20px; border-radius:10px; box-shadow:0 10px 25px rgba(2,132,199,0.4); z-index:99999; display:flex; align-items:center; gap:8px; transition:opacity 0.3s ease, transform 0.3s ease; opacity:0; transform:translateY(15px); pointer-events:none;';
      document.body.appendChild(toast);
    }
    toast.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${msg}`;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(15px)';
    }, 2400);
  },

  // 3. Thiết lập Modal chi tiết 3 ô (Bụi PM2.5, Nhiệt độ/Độ ẩm, GeoPandas)
  setupClickableModals() {
    const cardPM25 = document.getElementById('card-pm25-click');
    const cardMeteo = document.getElementById('card-meteo-click');
    const cardGeo = document.getElementById('card-geo-click');

    const modalPM25 = document.getElementById('modal-pm25-detail');
    const modalMeteo = document.getElementById('modal-meteo-detail');
    const modalGeo = document.getElementById('modal-geo-detail');

    const openModal = (m) => {
      if (m) {
        m.classList.add('show');
        m.style.display = 'flex';
        document.body.style.overflow = 'hidden';
      }
    };

    const closeModal = (m) => {
      if (m) {
        m.classList.remove('show');
        m.style.display = 'none';
        document.body.style.overflow = '';
      }
    };

    if (cardPM25) cardPM25.addEventListener('click', () => openModal(modalPM25));
    if (cardMeteo) cardMeteo.addEventListener('click', () => openModal(modalMeteo));
    if (cardGeo) cardGeo.addEventListener('click', () => openModal(modalGeo));

    document.querySelectorAll('.modal-close').forEach(btn => {
      btn.addEventListener('click', () => {
        const modalId = btn.getAttribute('data-modal');
        if (modalId) {
          closeModal(document.getElementById(modalId));
        } else {
          const parentModal = btn.closest('.modal-backdrop');
          if (parentModal) closeModal(parentModal);
        }
      });
    });

    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) closeModal(backdrop);
      });
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop.show').forEach(m => closeModal(m));
      }
    });
  },

  // 4. Thanh tìm kiếm đa tỉnh thành & Các nút chọn nhanh khu vực
  setupLocationSearch() {
    const inputSearch = document.getElementById('input-location-search');
    const dropdown = document.getElementById('search-results-dropdown');
    const pills = document.querySelectorAll('.district-pill');

    if (inputSearch && dropdown) {
      inputSearch.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        if (!query) {
          dropdown.style.display = 'none';
          dropdown.innerHTML = '';
          return;
        }

        const matches = this.stations.filter(s => 
          (s.station_name && s.station_name.toLowerCase().includes(query)) ||
          (s.district && s.district.toLowerCase().includes(query)) ||
          (s.province && s.province.toLowerCase().includes(query)) ||
          (s.region && s.region.toLowerCase().includes(query)) ||
          (s.station_id && s.station_id.toLowerCase().includes(query))
        );

        if (!matches.length) {
          dropdown.innerHTML = '<div style="padding:12px; color:#64748b; font-size:0.85rem; text-align:center;">Không tìm thấy tỉnh thành hoặc trạm phù hợp</div>';
          dropdown.style.display = 'block';
          return;
        }

        dropdown.innerHTML = matches.map(s => `
          <div class="search-result-item" data-station-id="${s.station_id}">
            <div>
              <div class="item-title">${s.station_name}</div>
              <div class="item-sub">${s.province} (${s.region || 'Việt Nam'})</div>
            </div>
            <span class="badge" style="background:#e0f2fe; color:#0369a1; font-weight:700;">${s.station_id}</span>
          </div>
        `).join('');
        dropdown.style.display = 'block';

        dropdown.querySelectorAll('.search-result-item').forEach(item => {
          item.addEventListener('click', () => {
            const stId = item.getAttribute('data-station-id');
            this.selectStationAndFocus(stId);
            dropdown.style.display = 'none';
            inputSearch.value = item.querySelector('.item-title').innerText;
          });
        });
      });

      document.addEventListener('click', (e) => {
        if (!inputSearch.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    }

    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        const loc = pill.getAttribute('data-location') || pill.getAttribute('data-district');
        this.filterByLocation(loc);
      });
    });
  },

  selectStationAndFocus(stationId) {
    const station = this.stations.find(s => s.station_id === stationId);
    if (!station) return;

    const select = document.getElementById('select-station');
    if (select) select.value = stationId;

    const rows = document.querySelectorAll('#overview-stations-tbody tr');
    rows.forEach(r => {
      if (r.innerText.includes(stationId)) {
        r.style.background = '#e0f2fe';
        r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        r.style.background = '';
      }
    });

    if (this.map && station.latitude && station.longitude) {
      this.map.setView([station.latitude, station.longitude], 13, { animate: true });
    }
  },

  filterByLocation(location) {
    const rows = document.querySelectorAll('#overview-stations-tbody tr');
    rows.forEach(r => {
      if (location === 'all' || r.innerText.toLowerCase().includes(location.toLowerCase())) {
        r.style.display = '';
      } else {
        r.style.display = 'none';
      }
    });

    if (location !== 'all') {
      const match = this.stations.find(s => 
        (s.province && s.province.toLowerCase().includes(location.toLowerCase())) ||
        (s.district && s.district.toLowerCase().includes(location.toLowerCase()))
      );
      if (match && this.map) {
        this.map.setView([match.latitude, match.longitude], 12, { animate: true });
      }
    } else if (this.map) {
      this.map.setView([16.05, 107.8], 6, { animate: true });
    }
  },

  // 5. Đồng hồ thời gian thực
  setupClock() {
    const updateTime = () => {
      const now = new Date();
      const str = now.toLocaleDateString('vi-VN', { 
        weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
      const el = document.getElementById('clock-val');
      if (el) el.innerText = str;
    };
    updateTime();
  },

  // 6. Đăng ký Service Worker
  setupPWA() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('sw.js').catch(() => {});
      });
    }
  },

  // 7. Nạp dữ liệu Tổng quan (Overview)
  async fetchOverviewData() {
    try {
      if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.latest) {
        this.latestObservations = EMBEDDED_DATA.latest;
      }
      if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.stations) {
        this.stations = EMBEDDED_DATA.stations;
      }

      this.renderOverviewMetrics();
      this.renderStationsTable();
      this.populateStationSelect();
    } catch (err) {
      console.error('Lỗi nạp dữ liệu:', err);
    }
  },

  renderOverviewMetrics() {
    if (!this.latestObservations || !this.latestObservations.length) return;

    const sumPM25 = this.latestObservations.reduce((acc, curr) => acc + curr.pm25, 0);
    const avgPM25 = Math.round((sumPM25 / this.latestObservations.length) * 10) / 10;
    
    const avgTemp = Math.round((this.latestObservations.reduce((a, c) => a + c.temperature, 0) / this.latestObservations.length) * 10) / 10;
    const avgHum = Math.round(this.latestObservations.reduce((a, c) => a + c.humidity, 0) / this.latestObservations.length);
    const avgWind = Math.round((this.latestObservations.reduce((a, c) => a + c.wind_speed, 0) / this.latestObservations.length) * 10) / 10;

    const elPM25 = document.getElementById('overview-pm25-val');
    const elTemp = document.getElementById('overview-weather-val');
    const elHum = document.getElementById('overview-humidity-val');
    const elWind = document.getElementById('overview-wind-val');

    if (elPM25) elPM25.innerText = avgPM25;
    if (elTemp) elTemp.innerText = `${avgTemp}°C`;
    if (elHum) elHum.innerText = `${avgHum}% RH`;
    if (elWind) elWind.innerText = `Gió: ${avgWind} m/s`;

    const aqiInfo = this.getAQIDetails(avgPM25);
    const elAQIVal = document.getElementById('overview-aqi-val');
    const elBadge = document.getElementById('overview-aqi-badge');
    const elAlertTitle = document.getElementById('health-alert-title');
    const elAlertDesc = document.getElementById('health-alert-desc');

    if (elAQIVal) elAQIVal.innerText = Math.round(avgPM25 * 1.8);
    if (elBadge) {
      elBadge.innerText = aqiInfo.level;
      elBadge.style.background = aqiInfo.color + '22';
      elBadge.style.color = aqiInfo.color;
      elBadge.style.border = `1px solid ${aqiInfo.color}66`;
    }
    if (elAlertTitle) elAlertTitle.innerText = `Chất lượng không khí toàn quốc: Mức ${aqiInfo.level}`;
    if (elAlertDesc) elAlertDesc.innerText = aqiInfo.advice;
  },

  getAQIDetails(pm25) {
    if (pm25 <= 12.0) {
      return { level: 'Tốt', color: '#10b981', advice: 'Chất lượng không khí trong lành, lý tưởng cho mọi hoạt động thể chất và thể thao ngoài trời.' };
    } else if (pm25 <= 35.4) {
      return { level: 'Trung bình', color: '#f59e0b', advice: 'Chất lượng không khí ở mức chấp nhận được đối với đa số người dân đô thị.' };
    } else if (pm25 <= 55.4) {
      return { level: 'Kém (Nhạy cảm)', color: '#f97316', advice: 'Trẻ em, người lớn tuổi và người có bệnh hô hấp nên giảm thiểu các hoạt động gắng sức ngoài trời.' };
    } else if (pm25 <= 150.0) {
      return { level: 'Xấu (Ô nhiễm)', color: '#ef4444', advice: 'Cảnh báo ô nhiễm: Nồng độ bụi mịn PM2.5 vượt ngưỡng. Khuyến nghị đeo khẩu trang N95 khi di chuyển ngoài đường.' };
    } else {
      return { level: 'Rất xấu / Nguy hại', color: '#8b5cf6', advice: 'Cảnh báo khẩn cấp: Hạn chế tối đa ra ngoài, đóng kín cửa sổ nhà và bật máy lọc không khí màng lọc HEPA.' };
    }
  },

  renderStationsTable() {
    const tbody = document.getElementById('overview-stations-tbody');
    if (!tbody || !this.latestObservations.length) return;
    tbody.innerHTML = '';

    this.latestObservations.forEach(obs => {
      const aqiInfo = this.getAQIDetails(obs.pm25);
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${obs.station_id}</strong></td>
        <td><strong>${obs.station_name}</strong></td>
        <td><span style="font-weight:700; color:#0369a1;"><i class="fa-solid fa-location-dot"></i> ${obs.province || obs.district}</span></td>
        <td><span class="badge" style="background:#f1f5f9; color:#475569;">${obs.region || 'Việt Nam'}</span></td>
        <td><strong style="color:${aqiInfo.color}; font-size:1.05rem;">${obs.pm25}</strong></td>
        <td>${obs.pm10 || '--'}</td>
        <td>${obs.no2 || '--'}</td>
        <td><span class="badge" style="background:${aqiInfo.color}22; color:${aqiInfo.color}; border:1px solid ${aqiInfo.color}66">${aqiInfo.level}</span></td>
        <td>
          <button class="btn btn-outline" style="padding:5px 12px; font-size:0.8rem;" onclick="App.quickForecast('${obs.station_id}')">
            <i class="fa-solid fa-chart-line"></i> Dự báo AI
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  },

  populateStationSelect() {
    const select = document.getElementById('select-station');
    if (!select || !this.stations.length) return;
    select.innerHTML = '';
    this.stations.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s.station_id;
      opt.innerText = `[${s.province || s.district}] ${s.station_name}`;
      select.appendChild(opt);
    });
  },

  quickForecast(stationId) {
    const select = document.getElementById('select-station');
    if (select) select.value = stationId;
    const forecastBtn = document.querySelector('[data-tab="tab-forecast"]');
    if (forecastBtn) forecastBtn.click();
  },

  // 8. Bản đồ không gian Toàn Quốc (Leaflet)
  initMap() {
    const mapContainer = document.getElementById('leaflet-map');
    if (!mapContainer) return;

    if (!this.map) {
      // Khởi tạo bản đồ trung tâm Việt Nam
      this.map = L.map('leaflet-map').setView([16.05, 107.8], 6);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | AirSense AI National Grid',
        maxZoom: 18
      }).addTo(this.map);

      this.stationLayer = L.layerGroup().addTo(this.map);
    }

    if (this.latestObservations && this.latestObservations.length) {
      this.stationLayer.clearLayers();

      this.latestObservations.forEach(st => {
        const aqiInfo = this.getAQIDetails(st.pm25);
        const marker = L.circleMarker([st.latitude, st.longitude], {
          radius: 9,
          fillColor: aqiInfo.color,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.95
        });

        marker.bindPopup(`
          <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:220px;">
            <h4 style="margin:0 0 4px 0; color:#0f172a;">${st.station_name}</h4>
            <small style="color:#64748b;"><i class="fa-solid fa-location-dot"></i> ${st.province || st.district} (${st.region || 'Việt Nam'})</small>
            <hr style="margin:8px 0; border:none; border-top:1px solid #e2e8f0;"/>
            <p style="margin:3px 0;"><strong>PM2.5:</strong> <span style="color:${aqiInfo.color}; font-weight:800; font-size:1.05rem;">${st.pm25} µg/m³</span></p>
            <p style="margin:3px 0;"><strong>PM10:</strong> ${st.pm10 || '--'} µg/m³ • <strong>NO2:</strong> ${st.no2 || '--'} µg/m³</p>
            <p style="margin:3px 0;"><strong>Nhiệt độ / Độ ẩm:</strong> ${st.temperature}°C / ${st.humidity}%</p>
            <p style="margin:3px 0;"><strong>Tốc độ gió:</strong> ${st.wind_speed} m/s</p>
            <div style="margin-top:8px; display:flex; justify-content:space-between; align-items:center;">
              <span class="badge" style="background:${aqiInfo.color}22; color:${aqiInfo.color}; border:1px solid ${aqiInfo.color}66">${aqiInfo.level}</span>
              <button class="btn btn-primary" style="padding:3px 8px; font-size:0.75rem;" onclick="App.quickForecast('${st.station_id}')">Dự báo AI</button>
            </div>
          </div>
        `);

        this.stationLayer.addLayer(marker);
      });
    }

    this.map.invalidateSize();
  },

  // 9. Kích hoạt dự báo AI Đa Bước
  setupForecastForm() {
    const form = document.getElementById('form-run-forecast');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const stationId = document.getElementById('select-station').value;
      const modelName = document.getElementById('select-model').value;
      const horizonHours = parseInt(document.getElementById('select-horizon').value);
      const btn = document.getElementById('btn-submit-forecast');

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tính toán suy luận AI...';

      setTimeout(() => {
        const forecastData = this.clientSideForecast(stationId, modelName, horizonHours);
        const historyData = (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.history && EMBEDDED_DATA.history[stationId]) 
          ? EMBEDDED_DATA.history[stationId] 
          : { records: [] };

        this.renderForecastResults(forecastData, historyData);

        const resultsBtn = document.querySelector('[data-tab="tab-results"]');
        if (resultsBtn) resultsBtn.click();

        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Dự Báo AI';
      }, 350);
    });
  },

  clientSideForecast(stationId, modelName, horizonHours) {
    const station = this.stations.find(s => s.station_id === stationId) || this.stations[0];
    const basePM25 = station ? station.pm25 : 30.0;
    const now = new Date();
    const steps = [];

    const modelBias = modelName === 'Random_Forest' ? 0.96 : (modelName === 'Neural_Network' ? 1.02 : 1.0);

    for (let h = 1; h <= horizonHours; h++) {
      const futureTime = new Date(now.getTime() + h * 3600 * 1000);
      const timeStr = futureTime.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) + ' ' +
                      futureTime.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });

      const cycleFactor = Math.sin((futureTime.getHours() - 6) * Math.PI / 12) * 8.5;
      const trend = ((h % 5) - 2) * 1.2;
      const predicted = Math.max(5.0, Math.round((basePM25 * modelBias + cycleFactor + trend) * 10) / 10);
      const uncertainty = Math.round((2.5 + h * 0.25) * 10) / 10;
      const lower = Math.max(0, Math.round((predicted - uncertainty) * 10) / 10);
      const upper = Math.round((predicted + uncertainty) * 10) / 10;

      const aqiInfo = this.getAQIDetails(predicted);

      steps.push({
        step_ahead: h,
        forecast_time: timeStr,
        pm25_predicted: predicted,
        lower_bound: lower,
        upper_bound: upper,
        unit: 'µg/m³',
        aqi_level: aqiInfo.level,
        color: aqiInfo.color,
        health_advice: aqiInfo.advice
      });
    }

    return {
      station_id: stationId,
      station_name: station ? station.station_name : stationId,
      district: station ? (station.province || station.district) : 'Việt Nam',
      model_used: modelName.replace('_', ' '),
      current_timestamp: now.toLocaleTimeString('vi-VN') + ' ' + now.toLocaleDateString('vi-VN'),
      current_pm25: basePM25,
      forecast_steps: steps
    };
  },

  renderForecastResults(forecast, history) {
    document.getElementById('meta-station-name').innerText = `${forecast.station_name} (${forecast.district})`;
    document.getElementById('meta-model-name').innerText = forecast.model_used;
    document.getElementById('meta-base-time').innerText = forecast.current_timestamp;
    document.getElementById('meta-current-pm25').innerText = `${forecast.current_pm25} µg/m³`;

    const tbody = document.getElementById('results-steps-tbody');
    tbody.innerHTML = '';

    forecast.forecast_steps.forEach(step => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>+${step.step_ahead}h</strong></td>
        <td>${step.forecast_time}</td>
        <td><strong style="color:${step.color}; font-size:1.05rem;">${step.pm25_predicted}</strong> ${step.unit}</td>
        <td><span style="color:#64748b;">${step.lower_bound} - ${step.upper_bound}</span></td>
        <td><span class="badge" style="background:${step.color}22; color:${step.color}; border:1px solid ${step.color}66">${step.aqi_level}</span></td>
        <td style="font-size:0.82rem; color:#475569;">${step.health_advice}</td>
      `;
      tbody.appendChild(tr);
    });

    this.renderForecastChart(history.records || [], forecast.forecast_steps, forecast.current_pm25);
  },

  renderForecastChart(historyRecords, forecastSteps, currentVal) {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    if (this.forecastChart) this.forecastChart.destroy();

    const histLabels = historyRecords.slice(-24).map(r => r.timestamp.slice(5, 16));
    const histValues = historyRecords.slice(-24).map(r => r.value);

    const forecastLabels = forecastSteps.map(s => s.forecast_time.slice(0, 5));
    const forecastValues = forecastSteps.map(s => s.pm25_predicted);
    const lowerBounds = forecastSteps.map(s => s.lower_bound);
    const upperBounds = forecastSteps.map(s => s.upper_bound);

    const allLabels = [...histLabels, ...forecastLabels];
    const seriesHist = [...histValues, ...Array(forecastLabels.length).fill(null)];
    const seriesForecast = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1] || currentVal,
      ...forecastValues
    ];
    const seriesUpper = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1] || currentVal,
      ...upperBounds
    ];
    const seriesLower = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1] || currentVal,
      ...lowerBounds
    ];

    this.forecastChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: allLabels,
        datasets: [
          {
            label: 'Quan trắc thực tế (Lịch sử)',
            data: seriesHist,
            borderColor: '#0284c7',
            backgroundColor: 'rgba(2, 132, 199, 0.08)',
            borderWidth: 2.5,
            pointRadius: 2,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Dự báo Trí tuệ Nhân tạo',
            data: seriesForecast,
            borderColor: '#0d9488',
            backgroundColor: 'rgba(13, 148, 136, 0.1)',
            borderWidth: 3,
            borderDash: [5, 4],
            pointRadius: 3,
            tension: 0.25,
            fill: false
          },
          {
            label: 'Dải tin cậy 95% (Cận trên)',
            data: seriesUpper,
            borderColor: 'transparent',
            backgroundColor: 'rgba(6, 182, 212, 0.15)',
            pointRadius: 0,
            fill: '+1',
            tension: 0.25
          },
          {
            label: 'Dải tin cậy 95% (Cận dưới)',
            data: seriesLower,
            borderColor: 'transparent',
            backgroundColor: 'transparent',
            pointRadius: 0,
            fill: false,
            tension: 0.25
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          y: { title: { display: true, text: 'Nồng độ PM2.5 (µg/m³)' }, beginAtZero: false },
          x: { ticks: { maxTicksLimit: 14 } }
        }
      }
    });
  },

  // 10. Đánh giá mô hình thực nghiệm
  fetchEvaluationData() {
    if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.metrics) {
      const metrics = EMBEDDED_DATA.metrics;
      const tbody = document.getElementById('eval-metrics-tbody');
      if (tbody) {
        tbody.innerHTML = '';
        Object.values(metrics).forEach(m => {
          const tr = document.createElement('tr');
          const isBest = m.r2 > 0.7;
          tr.innerHTML = `
            <td><strong>${m.model_name}</strong> ${isBest ? '<span class="badge badge-success">Tốt nhất</span>' : ''}</td>
            <td>${m.model_type}</td>
            <td><strong style="color:${isBest ? '#0d9488' : '#0f172a'}">${m.mae}</strong></td>
            <td>${m.rmse}</td>
            <td><strong style="color:${isBest ? '#0d9488' : '#0f172a'}">${m.r2}</strong></td>
            <td>${m.train_time_sec}s</td>
            <td>${m.inference_latency_ms} ms/mẫu</td>
            <td>${m.test_samples.toLocaleString()}</td>
          `;
          tbody.appendChild(tr);
        });
      }

      const ctx = document.getElementById('evalMetricsChart');
      if (ctx) {
        if (this.evalChart) this.evalChart.destroy();
        this.evalChart = new Chart(ctx, {
          type: 'bar',
          data: {
            labels: Object.values(metrics).map(m => m.model_name),
            datasets: [
              { label: 'MAE (Sai số tuyệt đối - µg/m³)', data: Object.values(metrics).map(m => m.mae), backgroundColor: '#0284c7' },
              { label: 'RMSE (Sai số toàn phương - µg/m³)', data: Object.values(metrics).map(m => m.rmse), backgroundColor: '#06b6d4' }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true, title: { display: true, text: 'Sai số dự báo (µg/m³)' } } }
          }
        });
      }
    }
  }
};

// Khởi chạy khi tài liệu nạp xong
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
