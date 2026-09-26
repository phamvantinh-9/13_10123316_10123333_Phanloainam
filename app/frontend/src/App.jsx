import React, { useEffect, useState } from 'react';

// Tên hiển thị tiếng Việt cho từng thuộc tính (khớp tên cột trong schema.json / DATA.md)
const FIELD_LABELS = {
  'cap-shape': 'Hình dạng mũ nấm',
  'cap-surface': 'Bề mặt mũ nấm',
  'cap-color': 'Màu mũ nấm',
  'bruises': 'Có vết bầm/dập khi chạm',
  'odor': 'Mùi',
  'gill-attachment': 'Cách phiến nấm gắn vào cuống',
  'gill-spacing': 'Khoảng cách giữa các phiến nấm',
  'gill-size': 'Kích thước phiến nấm',
  'gill-color': 'Màu phiến nấm',
  'stalk-shape': 'Hình dạng cuống nấm',
  'stalk-root': 'Dạng rễ/gốc cuống',
  'stalk-surface-above-ring': 'Bề mặt cuống phía trên vòng',
  'stalk-surface-below-ring': 'Bề mặt cuống phía dưới vòng',
  'stalk-color-above-ring': 'Màu cuống phía trên vòng',
  'stalk-color-below-ring': 'Màu cuống phía dưới vòng',
  'veil-color': 'Màu màng bao',
  'ring-number': 'Số lượng vòng trên cuống',
  'ring-type': 'Loại vòng',
  'spore-print-color': 'Màu bào tử in',
  'population': 'Mật độ quần thể xuất hiện',
  'habitat': 'Môi trường sống',
};

// Giải nghĩa từng giá trị mã hoá (1 ký tự) sang tiếng Việt dễ hiểu, cho từng thuộc tính.
// Nếu 1 giá trị nào đó không có trong bảng này, giao diện sẽ tự hiện lại đúng mã gốc.
const VALUE_LABELS = {
  'cap-shape': { b: 'Hình chuông', c: 'Hình nón', x: 'Hình lồi', f: 'Hình phẳng', k: 'Hình núm', s: 'Hình lõm' },
  'cap-surface': { f: 'Xơ', g: 'Có rãnh', y: 'Vảy', s: 'Nhẵn' },
  'cap-color': { n: 'Nâu', b: 'Vàng be', c: 'Quế', g: 'Xám', r: 'Xanh lá', p: 'Hồng', u: 'Tím', e: 'Đỏ', w: 'Trắng', y: 'Vàng' },
  'bruises': { t: 'Có vết bầm', f: 'Không có vết bầm' },
  'odor': { a: 'Hạnh nhân', l: 'Cỏ hồi', c: 'Nhựa (creosote)', y: 'Tanh', f: 'Hôi thối', m: 'Mốc', n: 'Không mùi', p: 'Hắc', s: 'Cay' },
  'gill-attachment': { a: 'Đính liền', d: 'Rủ xuống', f: 'Tự do', n: 'Có khía' },
  'gill-spacing': { c: 'Gần nhau', w: 'Dày đặc', d: 'Xa nhau' },
  'gill-size': { b: 'Rộng', n: 'Hẹp' },
  'gill-color': { k: 'Đen', n: 'Nâu', b: 'Vàng be', h: 'Socola', g: 'Xám', r: 'Xanh lá', o: 'Cam', p: 'Hồng', u: 'Tím', e: 'Đỏ', w: 'Trắng', y: 'Vàng' },
  'stalk-shape': { e: 'Phình to', t: 'Thon nhỏ' },
  'stalk-root': { b: 'Hình củ', c: 'Hình chuỳ', u: 'Hình cốc', e: 'Bằng nhau', z: 'Dạng rễ giả', r: 'Có rễ', '?': 'Không xác định' },
  'stalk-surface-above-ring': { f: 'Xơ', y: 'Vảy', k: 'Tơ mượt', s: 'Nhẵn' },
  'stalk-surface-below-ring': { f: 'Xơ', y: 'Vảy', k: 'Tơ mượt', s: 'Nhẵn' },
  'stalk-color-above-ring': { n: 'Nâu', b: 'Vàng be', c: 'Quế', g: 'Xám', o: 'Cam', p: 'Hồng', e: 'Đỏ', w: 'Trắng', y: 'Vàng' },
  'stalk-color-below-ring': { n: 'Nâu', b: 'Vàng be', c: 'Quế', g: 'Xám', o: 'Cam', p: 'Hồng', e: 'Đỏ', w: 'Trắng', y: 'Vàng' },
  'veil-color': { n: 'Nâu', o: 'Cam', w: 'Trắng', y: 'Vàng' },
  'ring-number': { n: 'Không có', o: 'Một', t: 'Hai' },
  'ring-type': { c: 'Dạng mạng nhện', e: 'Dễ biến mất', f: 'Loe ra', l: 'Lớn', n: 'Không có', p: 'Dạng dù', s: 'Dạng bao', z: 'Dạng đới' },
  'spore-print-color': { k: 'Đen', n: 'Nâu', b: 'Vàng be', h: 'Socola', r: 'Xanh lá', o: 'Cam', u: 'Tím', w: 'Trắng', y: 'Vàng' },
  'population': { a: 'Dồi dào', c: 'Thành cụm', n: 'Đông đúc', s: 'Rải rác', v: 'Vài cái', y: 'Đơn độc' },
  'habitat': { g: 'Đồng cỏ', l: 'Lá cây', m: 'Đồng hoang', p: 'Đường mòn', u: 'Đô thị', w: 'Bãi hoang', d: 'Rừng' },
};

function describeValue(fieldName, code) {
  const label = VALUE_LABELS[fieldName]?.[code];
  return label ? `${code} — ${label}` : code;
}

function App() {
  const [schema, setSchema] = useState(null);
  const [formData, setFormData] = useState({});
  const [loading, setLoading] = useState(false);
  const [schemaError, setSchemaError] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Tải schema.json (qua Backend -> AI Service) để tự sinh form đúng 21 thuộc tính
  useEffect(() => {
    fetch('/api/schema')
      .then((res) => {
        if (!res.ok) throw new Error('Không tải được schema từ server');
        return res.json();
      })
      .then((data) => {
        setSchema(data);
        const initial = {};
        data.features.forEach((f) => {
          initial[f.name] = f.allowed_values[0];
        });
        setFormData(initial);
      })
      .catch((err) => setSchemaError(err.message));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: formData }),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.detail || data.detail || 'Đã có lỗi xảy ra khi kết nối tới server phân loại!');
      }
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || 'Không thể kết nối đến AI Service hoặc Backend. Hãy kiểm tra lại container!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ maxWidth: '700px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <h1 style={{ textAlign: 'center', color: '#1f2937', marginBottom: '0.5rem' }}>
          🍄 Phân Loại Nấm Ăn Được Hay Có Độc
        </h1>
        <p style={{ textAlign: 'center', color: '#6b7280', marginBottom: '2rem' }}>
          Chọn đầy đủ {schema ? schema.features.length : 21} đặc điểm hình thái của cây nấm để hệ thống AI dự đoán.
        </p>

        {schemaError && (
          <div style={{ padding: '1rem', backgroundColor: '#fee2e2', color: '#b91c1c', borderRadius: '8px' }}>
            Không tải được form nhập liệu: {schemaError}. Kiểm tra lại Backend/AI Service đã chạy chưa.
          </div>
        )}

        {!schema && !schemaError && (
          <p style={{ textAlign: 'center', color: '#6b7280' }}>Đang tải form nhập liệu từ server...</p>
        )}

        {schema && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {schema.features.map((f) => (
              <div key={f.name} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                <label style={{ fontWeight: 'bold', color: '#374151' }}>
                  {FIELD_LABELS[f.name] || f.name} <span style={{ color: '#9ca3af', fontWeight: 'normal' }}>({f.name})</span>
                </label>
                <select
                  name={f.name}
                  value={formData[f.name] || ''}
                  onChange={handleChange}
                  style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}
                >
                  {f.allowed_values.map((v) => (
                    <option key={v} value={v}>{describeValue(f.name, v)}</option>
                  ))}
                </select>
              </div>
            ))}

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: '1rem',
                backgroundColor: loading ? '#9ca3af' : '#2563eb',
                color: 'white',
                padding: '0.75rem',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 'bold',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: '1rem',
              }}
            >
              {loading ? 'Đang phân tích đặc điểm...' : 'Dự Đoán Độc Tính Nấm'}
            </button>
          </form>
        )}

        {error && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#fee2e2', color: '#b91c1c', borderRadius: '8px' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: '1.5rem', padding: '1.5rem', backgroundColor: result.prediction === 'poisonous' ? '#fee2e2' : '#ecfdf5', borderRadius: '8px', border: `1px solid ${result.prediction === 'poisonous' ? '#dc2626' : '#10b981'}` }}>
            <h3 style={{ marginTop: 0, color: result.prediction === 'poisonous' ? '#991b1b' : '#065f46' }}>
              Kết quả dự đoán: {result.prediction === 'poisonous' ? '☠️ CÓ ĐỘC' : '✅ ĂN ĐƯỢC'}
            </h3>
            <p><strong>Độ tin cậy:</strong> {result.probability != null ? `${(result.probability * 100).toFixed(2)}%` : 'N/A'}</p>
            <p><strong>Model:</strong> {result.model_name} (v{result.model_version})</p>
            <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>request_id: {result.request_id}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
