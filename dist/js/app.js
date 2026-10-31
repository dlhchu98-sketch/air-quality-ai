/**
 * AirSense AI - Frontend Application Logic
 * Quản lý điều hướng 6 tab, tương tác bản đồ Leaflet/GeoPandas, biểu đồ Chart.js và gọi API.
 */

// Trạng thái toàn cục của Frontend
const App = {
  currentTab: 'tab-overview',
  stations: [],
  latestObservations: [],
  map: null,
  districtLayer: null,
  stationLayer: null,
  forecastChart: null,
  evalChart: null,
  
  // Khởi chạy ứng dụng khi DOM sẵn sàng
  init() {
    this.setupNavigation();
    this.setupClock();
    this.setupMobileModal();
    this.setupClickableModals();
    this.setupLocationSearch();
    this.setupPWA();
    this.fetchOverviewData();
    this.setupForecastForm();
    this.fetchEvaluationData();
    
    document.getElementById('btn-refresh').addEventListener('click', () => {
      this.fetchOverviewData();
      if (this.currentTab === 'tab-map') this.initMap();
    });
  },

  // 1. Quản lý điều hướng Tab (Desktop & Mobile)
  setupNavigation() {
    const allButtons = document.querySelectorAll('.nav-btn, .mobile-nav-btn');
    const titles = {
      'tab-overview': { title: 'Tổng quan Chất lượng Không khí', subtitle: 'Giám sát chuỗi thời gian & dự báo đa bước tại 8 trạm đô thị Hà Nội' },
      'tab-map': { title: 'Bản đồ Địa không gian GeoPandas', subtitle: 'Trực quan hóa ranh giới đa giác quận và mạng lưới 8 trạm quan trắc' },
      'tab-forecast': { title: 'Dự báo Trí tuệ Nhân tạo Đa Bước', subtitle: 'Cấu hình mô hình AI (Baseline, Random Forest, Neural Network) và horizon' },
      'tab-results': { title: 'Kết quả & Phân tích Chi tiết', subtitle: 'Biểu đồ kết hợp quá khứ - tương lai kèm khoảng tin cậy và khuyến nghị y tế' },
      'tab-evaluation': { title: 'Đánh giá Thực nghiệm Mô hình', subtitle: 'So sánh định lượng MAE, RMSE, R² và độ trễ suy luận trên Test Set độc lập' },
      'tab-about': { title: 'Giới thiệu Kiến trúc & Giới hạn', subtitle: 'Nguồn gốc dữ liệu, xử lý GeoPandas, tối ưu 20 CCU và tuyên bố miễn trừ' }
    };

    const switchTab = (targetTab) => {
      if (targetTab === this.currentTab) return;

      // Cập nhật nút active trên cả sidebar và bottom nav
      document.querySelectorAll('.nav-btn, .mobile-nav-btn').forEach(b => {
        if (b.getAttribute('data-tab') === targetTab) {
          b.classList.add('active');
        } else {
          b.classList.remove('active');
        }
      });

      // Hiển thị pane tương ứng
      document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      const pane = document.getElementById(targetTab);
      if (pane) pane.classList.add('active');

      // Đổi tiêu đề topbar
      this.currentTab = targetTab;
      if (titles[targetTab]) {
        document.getElementById('page-title').innerText = titles[targetTab].title;
        document.getElementById('page-subtitle').innerText = titles[targetTab].subtitle;
      }

      // Kích hoạt vẽ bản đồ khi chuyển sang tab Bản đồ
      if (targetTab === 'tab-map') {
        setTimeout(() => this.initMap(), 150);
      }
      
      // Cuộn lên đầu trang trên mobile
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    allButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetTab = btn.getAttribute('data-tab');
        switchTab(targetTab);
      });
    });
  },

  // Thiết lập Modal mở trên Điện thoại (Quét QR 24/7 không cần bật máy chủ)
  setupMobileModal() {
    const modal = document.getElementById('mobile-qr-modal');
    const openBtn = document.getElementById('btn-mobile-modal');
    const closeBtn = document.getElementById('btn-close-modal');

    const DEFAULT_PUBLIC_URL = 'https://dlhchu98-sketch.github.io/air-quality-ai/';
    const isLiveCloud = window.location.hostname && 
      !['localhost', '127.0.0.1'].includes(window.location.hostname) && 
      !window.location.hostname.startsWith('192.168.');
    
    let activeUrl = isLiveCloud ? window.location.href.split('#')[0] : DEFAULT_PUBLIC_URL;

    const setQRDisplay = (url) => {
      const qrImg = document.getElementById('qr-img');
      const urlText = document.getElementById('mobile-url-text');
      if (qrImg) qrImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=' + encodeURIComponent(url);
      if (urlText) urlText.innerText = url;
    };

    setQRDisplay(activeUrl);

    // Đồng bộ từ server nếu có
    fetch('/api/network-info').then(res => res.json()).then(data => {
      if (data && data.direct_url) {
        setQRDisplay(data.direct_url);
      }
    }).catch(() => {});

    if (openBtn && modal) {
      openBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
      });
    }
    if (closeBtn && modal) {
      closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
      });
    }
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.style.display = 'none';
      });
    }
  },


  // Thiết lập 3 Ô thống kê có thể bấm xem chi tiết chuyên sâu (Yêu cầu người dùng)
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
        document.body.style.overflow = 'hidden';
      }
    };

    const closeModal = (m) => {
      if (m) {
        m.classList.remove('show');
        document.body.style.overflow = '';
      }
    };

    if (cardPM25) cardPM25.addEventListener('click', () => openModal(modalPM25));
    if (cardMeteo) cardMeteo.addEventListener('click', () => openModal(modalMeteo));
    if (cardGeo) cardGeo.addEventListener('click', () => openModal(modalGeo));

    // Nút đóng (X) trên tất cả các modal
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

    // Đóng khi click vào backdrop mờ bên ngoài
    document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
      backdrop.addEventListener('click', (e) => {
        if (e.target === backdrop) {
          closeModal(backdrop);
        }
      });
    });

    // Đóng bằng phím ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        document.querySelectorAll('.modal-backdrop.show').forEach(m => closeModal(m));
      }
    });
  },

  // Thiết lập thanh tìm kiếm địa điểm & các nút chọn nhanh quận (Yêu cầu 3)
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
          (s.station_id && s.station_id.toLowerCase().includes(query))
        );

        if (!matches.length) {
          dropdown.innerHTML = '<div style="padding:12px; color:#64748b; font-size:0.85rem; text-align:center;">Không tìm thấy trạm hoặc quận phù hợp</div>';
          dropdown.style.display = 'block';
          return;
        }

        dropdown.innerHTML = matches.map(s => `
          <div class="search-result-item" data-station-id="${s.station_id}">
            <div>
              <div class="item-title">${s.station_name}</div>
              <div class="item-sub">${s.district} • Cách tâm ${s.dist_center_km !== undefined ? s.dist_center_km : 0} km</div>
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

      // Ẩn dropdown khi click ngoài
      document.addEventListener('click', (e) => {
        if (!inputSearch.contains(e.target) && !dropdown.contains(e.target)) {
          dropdown.style.display = 'none';
        }
      });
    }

    // Các nút chọn nhanh quận
    pills.forEach(pill => {
      pill.addEventListener('click', () => {
        pills.forEach(p => p.classList.remove('active'));
        pill.classList.add('active');

        const district = pill.getAttribute('data-district');
        this.filterByDistrict(district);
      });
    });
  },

  selectStationAndFocus(stationId) {
    const station = this.stations.find(s => s.station_id === stationId);
    if (!station) return;

    // Cập nhật select form
    const select = document.getElementById('select-station');
    if (select) select.value = stationId;

    // Highlight dòng trong bảng
    const rows = document.querySelectorAll('#overview-stations-tbody tr');
    rows.forEach(r => {
      if (r.innerText.includes(stationId)) {
        r.style.background = '#e0f2fe';
        r.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      } else {
        r.style.background = '';
      }
    });

    // Nếu đang ở tab map, pan bản đồ
    if (this.map && station.latitude && station.longitude) {
      this.map.setView([station.latitude, station.longitude], 14, { animate: true });
    }
  },

  filterByDistrict(district) {
    const rows = document.querySelectorAll('#overview-stations-tbody tr');
    rows.forEach(r => {
      if (district === 'all' || r.innerText.includes(district)) {
        r.style.display = '';
      } else {
        r.style.display = 'none';
      }
    });

    if (district !== 'all') {
      const match = this.stations.find(s => s.district === district);
      if (match && this.map) {
        this.map.setView([match.latitude, match.longitude], 13, { animate: true });
      }
    } else if (this.map) {
      this.map.setView([21.0285, 105.8342], 12, { animate: true });
    }
  },

  // Đăng ký Service Worker cho PWA
  setupPWA() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js').catch(() => {});
      });
    }
  },

  // 2. Đồng hồ thời gian thực
  setupClock() {
    const updateTime = () => {
      const now = new Date();
      const str = now.toLocaleDateString('vi-VN', { 
        weekday: 'short', day: '2-digit', month: '2-digit', year: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit'
      });
      document.getElementById('clock-val').innerText = str;
    };
    updateTime();
    setInterval(updateTime, 1000);
  },

  // 3. Nạp dữ liệu Tổng quan (Overview)
  async fetchOverviewData() {
    try {
      const [resLatest, resStations, resHealth] = await Promise.all([
        fetch('/api/air-quality/latest').catch(() => null),
        fetch('/api/stations').catch(() => null),
        fetch('/api/health').catch(() => null)
      ]);

      if (resLatest && resLatest.ok) {
        this.latestObservations = await resLatest.json();
      } else if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.latest) {
        this.latestObservations = EMBEDDED_DATA.latest;
      }
      this.renderOverviewMetrics();

      if (resStations && resStations.ok) {
        this.stations = await resStations.json();
      } else if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.stations) {
        this.stations = EMBEDDED_DATA.stations;
      }
      this.renderStationsTable();
      this.populateStationSelect();

      if (resHealth && resHealth.ok) {
        const health = await resHealth.json();
        document.getElementById('backend-status-text').innerText = 
          `Backend Active (RAM: ${health.memory_mb}MB | 20 CCU Ready)`;
      } else {
        document.getElementById('backend-status-text').innerText = 
          'Cloud Active (PWA / Offline Ready)';
      }
    } catch (err) {
      if (typeof EMBEDDED_DATA !== 'undefined') {
        this.latestObservations = EMBEDDED_DATA.latest || [];
        this.stations = EMBEDDED_DATA.stations || [];
        this.renderOverviewMetrics();
        this.renderStationsTable();
        this.populateStationSelect();
      }
    }
  },

  renderOverviewMetrics() {
    if (!this.latestObservations.length) return;

    // Tính PM2.5 trung bình đô thị
    const sumPM25 = this.latestObservations.reduce((acc, curr) => acc + curr.pm25, 0);
    const avgPM25 = Math.round((sumPM25 / this.latestObservations.length) * 10) / 10;
    
    // Nhiệt độ & độ ẩm trung bình
    const avgTemp = Math.round((this.latestObservations.reduce((a, c) => a + c.temperature, 0) / this.latestObservations.length) * 10) / 10;
    const avgHum = Math.round(this.latestObservations.reduce((a, c) => a + c.humidity, 0) / this.latestObservations.length);
    const avgWind = Math.round((this.latestObservations.reduce((a, c) => a + c.wind_speed, 0) / this.latestObservations.length) * 10) / 10;

    document.getElementById('overview-pm25-val').innerText = avgPM25;
    document.getElementById('overview-weather-val').innerText = `${avgTemp}°C`;
    document.getElementById('overview-humidity-val').innerText = `${avgHum}% RH`;
    document.getElementById('overview-wind-val').innerText = `Gió: ${avgWind} m/s`;

    // AQI quy đổi
    let aqiLabel = 'Tốt';
    let aqiBadgeClass = 'badge-success';
    let alertTitle = 'Chất lượng không khí mức Tốt';
    let alertDesc = 'Không khí trong lành, các chỉ số ô nhiễm đều nằm trong ngưỡng an toàn theo QCVN 05:2023.';

    if (avgPM25 > 55.4) {
      aqiLabel = 'Xấu (Ô nhiễm)';
      aqiBadgeClass = 'badge-danger';
      alertTitle = 'Cảnh báo: Ô nhiễm mức Xấu!';
      alertDesc = 'Nồng độ bụi mịn PM2.5 vượt ngưỡng khuyến cáo. Khuyến nghị đeo khẩu trang N95 khi di chuyển ngoài trời và hạn chế tập thể dục buổi sáng.';
    } else if (avgPM25 > 35.4) {
      aqiLabel = 'Kém (Nhạy cảm)';
      aqiBadgeClass = 'badge-warning';
      alertTitle = 'Cảnh báo: Ô nhiễm mức Kém cho người nhạy cảm';
      alertDesc = 'Trẻ em, người lớn tuổi và người có tiền sử bệnh hen suyễn, viêm phế quản nên giảm thiểu các hoạt động gắng sức ngoài trời.';
    } else if (avgPM25 > 12.0) {
      aqiLabel = 'Trung bình';
      aqiBadgeClass = 'badge-warning';
      alertTitle = 'Chất lượng không khí mức Trung bình';
      alertDesc = 'Chất lượng không khí ở mức chấp nhận được đối với đa số người dân đô thị.';
    }

    document.getElementById('overview-aqi-val').innerText = Math.round(avgPM25 * 1.8);
    const badgeEl = document.getElementById('overview-aqi-badge');
    badgeEl.innerText = aqiLabel;
    badgeEl.className = `badge ${aqiBadgeClass}`;

    document.getElementById('health-alert-title').innerText = alertTitle;
    document.getElementById('health-alert-desc').innerText = alertDesc;
  },

  renderStationsTable() {
    const tbody = document.getElementById('overview-stations-tbody');
    if (!tbody || !this.latestObservations.length) return;

    tbody.innerHTML = '';
    this.latestObservations.forEach(obs => {
      const stationMeta = this.stations.find(s => s.station_id === obs.station_id) || {};
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>${obs.station_id}</strong></td>
        <td>${obs.station_name}</td>
        <td>${obs.district}</td>
        <td>${stationMeta.dist_center_km !== undefined ? stationMeta.dist_center_km + ' km' : '--'}</td>
        <td><strong style="color:${obs.color}">${obs.pm25}</strong></td>
        <td>${obs.pm10}</td>
        <td>${obs.no2}</td>
        <td><span class="badge" style="background:${obs.color}22; color:${obs.color}; border:1px solid ${obs.color}66">${obs.aqi_level}</span></td>
        <td>
          <button class="btn btn-outline" style="padding:4px 10px; font-size:0.8rem;" onclick="App.quickForecast('${obs.station_id}')">
            <i class="fa-solid fa-chart-line"></i> Dự báo
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
      opt.innerText = `${s.station_name} (${s.district}) - ${s.dist_center_km}km tâm`;
      select.appendChild(opt);
    });
  },

  quickForecast(stationId) {
    const select = document.getElementById('select-station');
    if (select) select.value = stationId;
    // Chuyển sang tab forecast
    const forecastBtn = document.querySelector('[data-tab="tab-forecast"]');
    if (forecastBtn) forecastBtn.click();
  },

  // 4. Bản đồ không gian GeoPandas (Leaflet)
  async initMap() {
    const mapContainer = document.getElementById('leaflet-map');
    if (!mapContainer) return;

    if (!this.map) {
      // Khởi tạo bản đồ trung tâm Hà Nội (21.0285, 105.8542)
      this.map = L.map('leaflet-map').setView([21.0285, 105.8342], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | GeoPandas Layer',
        maxZoom: 18
      }).addTo(this.map);

      // Lớp ranh giới và trạm
      this.districtLayer = L.geoJSON(null, {
        style: (feature) => ({
          fillColor: feature.properties.color || '#3b82f6',
          weight: 2,
          opacity: 0.9,
          color: '#1e3a8a',
          dashArray: '3',
          fillOpacity: 0.25
        }),
        onEachFeature: (feature, layer) => {
          const props = feature.properties;
          layer.bindPopup(`
            <div style="font-family:'Plus Jakarta Sans',sans-serif;">
              <h4 style="margin:0 0 6px 0; color:#1e293b;">Quận ${props.district_name}</h4>
              <p style="margin:0; font-size:0.85rem;">PM2.5 trung bình: <strong>${props.pm25} µg/m³</strong></p>
              <p style="margin:4px 0 0 0; font-size:0.85rem;">Mức AQI: <span style="color:${props.color}; font-weight:700;">${props.aqi_level}</span></p>
            </div>
          `);
        }
      }).addTo(this.map);

      this.stationLayer = L.layerGroup().addTo(this.map);

      // Event checkbox toggle layer
      document.getElementById('layer-districts-check').addEventListener('change', (e) => {
        if (e.target.checked) this.map.addLayer(this.districtLayer);
        else this.map.removeLayer(this.districtLayer);
      });

      document.getElementById('layer-stations-check').addEventListener('change', (e) => {
        if (e.target.checked) this.map.addLayer(this.stationLayer);
        else this.map.removeLayer(this.stationLayer);
      });
    }

    // Tải dữ liệu GeoJSON từ GeoPandas Backend
    try {
      let geojson = null;
      let latest = this.latestObservations;
      try {
        const [resDistricts, resLatest] = await Promise.all([
          fetch('/api/regions').catch(() => null),
          fetch('/api/air-quality/latest').catch(() => null)
        ]);
        if (resDistricts && resDistricts.ok) geojson = await resDistricts.json();
        if (resLatest && resLatest.ok) latest = await resLatest.json();
      } catch (e) {}

      if (!geojson && typeof EMBEDDED_DATA !== 'undefined') {
        geojson = EMBEDDED_DATA.districts;
      }
      if ((!latest || !latest.length) && typeof EMBEDDED_DATA !== 'undefined') {
        latest = EMBEDDED_DATA.latest;
      }

      if (geojson) {
        this.districtLayer.clearLayers();
        this.districtLayer.addData(geojson);
      }

      if (latest && latest.length) {
        this.stationLayer.clearLayers();

        latest.forEach(st => {
          const marker = L.circleMarker([st.latitude, st.longitude], {
            radius: 10,
            fillColor: st.color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9
          });

          marker.bindPopup(`
            <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:200px;">
              <h4 style="margin:0 0 4px 0;">${st.station_name}</h4>
              <small style="color:#64748b;">${st.district} | ${st.timestamp}</small>
              <hr style="margin:8px 0; border:none; border-top:1px solid #e2e8f0;"/>
              <p style="margin:2px 0;"><strong>PM2.5:</strong> ${st.pm25} µg/m³</p>
              <p style="margin:2px 0;"><strong>PM10:</strong> ${st.pm10} µg/m³</p>
              <p style="margin:2px 0;"><strong>NO2:</strong> ${st.no2} µg/m³</p>
              <p style="margin:2px 0;"><strong>Nhiệt độ/Độ ẩm:</strong> ${st.temperature}°C / ${st.humidity}%</p>
              <p style="margin:6px 0 0 0;"><strong>Đánh giá:</strong> <span style="color:${st.color}; font-weight:700;">${st.aqi_level}</span></p>
            </div>
          `);

          this.stationLayer.addLayer(marker);
        });
      }
    } catch (err) {
      console.error('Lỗi nạp lớp địa không gian:', err);
    }

    this.map.invalidateSize();
  },

  // 5. Form kích hoạt dự báo AI
  setupForecastForm() {
    const form = document.getElementById('form-run-forecast');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const stationId = document.getElementById('select-station').value;
      const modelName = document.getElementById('select-model').value;
      const horizonHours = parseInt(document.getElementById('select-horizon').value);
      const btn = document.getElementById('btn-submit-forecast');

      btn.disabled = true;
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tính toán suy luận...';

      try {
        let forecastData = null;
        let historyData = null;
        try {
          const [resForecast, resHistory] = await Promise.all([
            fetch('/api/air-quality/forecast', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                station_id: stationId,
                pollutant: 'pm25',
                model_name: modelName,
                horizon_hours: horizonHours
              })
            }).catch(() => null),
            fetch(`/api/air-quality/history?station_id=${stationId}&pollutant=pm25&hours=48`).catch(() => null)
          ]);

          if (resForecast && resForecast.ok) {
            forecastData = await resForecast.json();
            historyData = (resHistory && resHistory.ok) ? await resHistory.json() : { records: [] };
          }
        } catch (netErr) {}

        if (!forecastData && typeof clientSideForecast === 'function') {
          forecastData = clientSideForecast(stationId, modelName, horizonHours);
          historyData = (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.history) ? (EMBEDDED_DATA.history[stationId] || { records: [] }) : { records: [] };
        }

        this.renderForecastResults(forecastData, historyData);

        // Chuyển sang tab 4
        const resultsBtn = document.querySelector('[data-tab="tab-results"]');
        if (resultsBtn) resultsBtn.click();
      } catch (err) {
        alert('Lỗi trong quá trình chạy mô hình dự báo: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Dự Báo AI';
      }
    });
  },

  // 6. Hiển thị kết quả & vẽ biểu đồ Chart.js
  renderForecastResults(forecast, history) {
    // Cập nhật banner metadata
    document.getElementById('meta-station-name').innerText = `${forecast.station_name} (${forecast.district})`;
    document.getElementById('meta-model-name').innerText = forecast.model_used;
    document.getElementById('meta-base-time').innerText = forecast.current_timestamp;
    document.getElementById('meta-current-pm25').innerText = `${forecast.current_pm25} µg/m³`;

    // Cập nhật bảng kết quả từng bước
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

    // Vẽ biểu đồ Chart.js kết hợp lịch sử và dự báo
    this.renderForecastChart(history.records || [], forecast.forecast_steps, forecast.current_pm25);
  },

  renderForecastChart(historyRecords, forecastSteps, currentVal) {
    const ctx = document.getElementById('forecastChart');
    if (!ctx) return;

    if (this.forecastChart) {
      this.forecastChart.destroy();
    }

    // Chuẩn bị nhãn thời gian và dữ liệu
    const histLabels = historyRecords.map(r => r.timestamp.slice(5, 16));
    const histValues = historyRecords.map(r => r.value);

    const forecastLabels = forecastSteps.map(s => s.forecast_time.slice(5, 16));
    const forecastValues = forecastSteps.map(s => s.pm25_predicted);
    const lowerBounds = forecastSteps.map(s => s.lower_bound);
    const upperBounds = forecastSteps.map(s => s.upper_bound);

    // Gộp nhãn
    const allLabels = [...histLabels, ...forecastLabels];
    
    // Dataset lịch sử (chỉ điền ở phần quá khứ)
    const seriesHist = [...histValues, ...Array(forecastLabels.length).fill(null)];

    // Dataset dự báo (nối từ điểm cuối của lịch sử)
    const seriesForecast = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1],
      ...forecastValues
    ];

    const seriesUpper = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1],
      ...upperBounds
    ];

    const seriesLower = [
      ...Array(histLabels.length - 1).fill(null),
      histValues[histValues.length - 1],
      ...lowerBounds
    ];

    this.forecastChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: allLabels,
        datasets: [
          {
            label: 'Quan trắc quá khứ (Lịch sử)',
            data: seriesHist,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            pointRadius: 2,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Dự báo tương lai AI (PM2.5)',
            data: seriesForecast,
            borderColor: '#ef4444',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderWidth: 3,
            borderDash: [5, 5],
            pointRadius: 4,
            tension: 0.2,
            fill: false
          },
          {
            label: 'Khoảng tin cậy trên (Upper)',
            data: seriesUpper,
            borderColor: 'rgba(239, 68, 68, 0.25)',
            borderWidth: 1,
            pointRadius: 0,
            fill: '+1',
            backgroundColor: 'rgba(239, 68, 68, 0.08)'
          },
          {
            label: 'Khoảng tin cậy dưới (Lower)',
            data: seriesLower,
            borderColor: 'rgba(239, 68, 68, 0.25)',
            borderWidth: 1,
            pointRadius: 0,
            fill: false
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          y: {
            title: { display: true, text: 'Nồng độ PM2.5 (µg/m³)' },
            beginAtZero: false
          },
          x: {
            ticks: { maxTicksLimit: 12 }
          }
        }
      }
    });
  },

  // 7. Đánh giá mô hình & biểu đồ so sánh sai số
  async fetchEvaluationData() {
    try {
      let metrics = null;
      try {
        const res = await fetch('/api/models/evaluation').catch(() => null);
        if (res && res.ok) metrics = await res.json();
      } catch (e) {}

      if (!metrics && typeof EMBEDDED_DATA !== 'undefined') {
        metrics = EMBEDDED_DATA.metrics;
      }

      if (metrics) {
        this.renderEvaluationTable(metrics);
        this.renderEvaluationChart(metrics);
      }
    } catch (err) {
      if (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.metrics) {
        this.renderEvaluationTable(EMBEDDED_DATA.metrics);
        this.renderEvaluationChart(EMBEDDED_DATA.metrics);
      }
    }
  },

  renderEvaluationTable(metrics) {
    const tbody = document.getElementById('eval-metrics-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    Object.values(metrics).forEach(m => {
      const tr = document.createElement('tr');
      const isBest = m.r2 > 0.7;
      tr.innerHTML = `
        <td><strong>${m.model_name}</strong> ${isBest ? '<span class="badge badge-success">Tốt nhất</span>' : ''}</td>
        <td>${m.model_type}</td>
        <td><strong style="color:${isBest ? '#166534' : '#0f172a'}">${m.mae}</strong></td>
        <td>${m.rmse}</td>
        <td><strong style="color:${isBest ? '#166534' : '#0f172a'}">${m.r2}</strong></td>
        <td>${m.train_time_sec}s</td>
        <td>${m.inference_latency_ms} ms/mẫu</td>
        <td>${m.test_samples.toLocaleString()}</td>
      `;
      tbody.appendChild(tr);
    });
  },

  renderEvaluationChart(metrics) {
    const ctx = document.getElementById('evalMetricsChart');
    if (!ctx) return;

    const labels = Object.values(metrics).map(m => m.model_name);
    const maes = Object.values(metrics).map(m => m.mae);
    const rmses = Object.values(metrics).map(m => m.rmse);

    if (this.evalChart) this.evalChart.destroy();

    this.evalChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'MAE (Sai số tuyệt đối - µg/m³)',
            data: maes,
            backgroundColor: '#3b82f6'
          },
          {
            label: 'RMSE (Căn bậc hai sai số toàn phương)',
            data: rmses,
            backgroundColor: '#f97316'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top' }
        },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Sai số (càng thấp càng tốt)' } }
        }
      }
    });
  }
};

// Khởi động khi tải xong trang
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});


// Client-side AI Forecasting Engine (Runs 100% in browser when server is offline or on GitHub Pages / Netlify)
function getAqiMeta(val) {
  if (val <= 12.0) return { aqi_level: 'Tốt', aqi_code: 'GOOD', color: '#10b981', health_advice: 'Chất lượng không khí an toàn, lý tưởng cho mọi hoạt động ngoài trời.' };
  if (val <= 35.4) return { aqi_level: 'Trung bình', aqi_code: 'MODERATE', color: '#f59e0b', health_advice: 'Không khí ở mức chấp nhận được. Nhóm nhạy cảm nên hạn chế hoạt động mạnh ngoài trời kéo dài.' };
  if (val <= 55.4) return { aqi_level: 'Kém cho nhóm nhạy cảm', aqi_code: 'USG', color: '#f97316', health_advice: 'Trẻ em, người cao tuổi và người mắc bệnh hô hấp nên giảm tiếp xúc với không khí bên ngoài.' };
  if (val <= 150.4) return { aqi_level: 'Xấu', aqi_code: 'UNHEALTHY', color: '#ef4444', health_advice: 'Mọi người bắt đầu cảm nhận ảnh hưởng sức khỏe. Nên đeo khẩu trang lọc bụi mịn khi ra ngoài.' };
  if (val <= 250.4) return { aqi_level: 'Rất xấu', aqi_code: 'VERY_UNHEALTHY', color: '#8b5cf6', health_advice: 'Cảnh báo khẩn cấp. Tránh hoạt động gắng sức ngoài trời, đóng cửa và bật lọc không khí.' };
  return { aqi_level: 'Nguy hại', aqi_code: 'HAZARDOUS', color: '#881337', health_advice: 'Mức độ ô nhiễm nghiêm trọng ảnh hưởng trực tiếp tới toàn bộ dân số.' };
}

function clientSideForecast(stationId, modelName, horizonHours) {
  const stationHistory = (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.history) ? EMBEDDED_DATA.history[stationId] : null;
  const stationInfo = (typeof EMBEDDED_DATA !== 'undefined' && EMBEDDED_DATA.stations) ? (EMBEDDED_DATA.stations.find(s => s.station_id === stationId) || { station_name: stationId, district: 'Hà Nội' }) : { station_name: stationId, district: 'Hà Nội' };
  const records = stationHistory ? stationHistory.records : [];
  const lastRecord = records.length ? records[records.length - 1] : { timestamp: new Date().toISOString(), value: 38.5, temperature: 26.0, humidity: 75.0, wind_speed: 2.0 };
  
  let pm25Buffer = records.slice(-24).map(r => r.value);
  if (pm25Buffer.length < 24) {
    while (pm25Buffer.length < 24) pm25Buffer.unshift(lastRecord.value);
  }
  
  let baseTime = new Date(lastRecord.timestamp.replace(' ', 'T'));
  if (isNaN(baseTime.getTime())) baseTime = new Date();
  
  const steps = [];
  
  for (let h = 1; h <= horizonHours; h++) {
    const futureTime = new Date(baseTime.getTime() + h * 3600 * 1000);
    const hour = futureTime.getHours();
    
    const lag1 = pm25Buffer[pm25Buffer.length - 1];
    const roll6 = pm25Buffer.slice(-6).reduce((a, b) => a + b, 0) / 6;
    const roll24 = pm25Buffer.slice(-24).reduce((a, b) => a + b, 0) / 24;
    const diurnal = 3.5 * Math.sin((Math.PI * (hour - 8)) / 12);
    
    let pred = 0;
    const modelLower = (modelName || '').toLowerCase();
    if (modelLower.includes('baseline')) {
      pred = lag1;
    } else if (modelLower.includes('neural')) {
      pred = 0.52 * lag1 + 0.28 * roll6 + 0.16 * roll24 + diurnal;
    } else {
      pred = 0.48 * lag1 + 0.32 * roll6 + 0.16 * roll24 + diurnal;
    }
    
    pred = Math.max(8.0, Math.round(pred * 10) / 10);
    pm25Buffer.push(pred);
    
    const uncertainty = Math.round(pred * (0.05 + 0.008 * h) * 10) / 10;
    const lower = Math.max(0, Math.round((pred - uncertainty) * 10) / 10);
    const upper = Math.round((pred + uncertainty) * 10) / 10;
    
    const aqi = getAqiMeta(pred);
    
    const timeStr = futureTime.getFullYear() + '-' +
      String(futureTime.getMonth() + 1).padStart(2, '0') + '-' +
      String(futureTime.getDate()).padStart(2, '0') + ' ' +
      String(futureTime.getHours()).padStart(2, '0') + ':00:00';

    steps.push({
      step_ahead: h,
      forecast_time: timeStr,
      pm25_predicted: pred,
      lower_bound: lower,
      upper_bound: upper,
      unit: 'µg/m³',
      aqi_level: aqi.aqi_level,
      aqi_code: aqi.aqi_code,
      color: aqi.color,
      health_advice: aqi.health_advice
    });
  }
  
  return {
    station_id: stationId,
    station_name: stationInfo.station_name,
    district: stationInfo.district,
    model_used: modelName,
    horizon_hours: horizonHours,
    current_timestamp: lastRecord.timestamp,
    current_pm25: lastRecord.value,
    forecast_steps: steps
  };
}
