import React, { useState } from 'react';

function App() {
  const [formData, setFormData] = useState({
    cap_shape: 'convex',
    cap_surface: 'smooth',
    cap_color: 'brown',
    odor: 'none',
    habitat: 'woods'
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Dùng đường dẫn tương đối để Nginx tự động proxy request sang backend trong Docker
      const apiEndpoint = '/predict';

      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error('Đã có lỗi xảy ra khi kết nối tới server phân loại!');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError('Không thể kết nối đến AI Service hoặc Backend. Hãy kiểm tra lại container!');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6', padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <div style={{ maxWidth: '650px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
        <h1 style={{ textAlign: 'center', color: '#1f2937', marginBottom: '0.5rem' }}>
          🍄 Phân Loại Nấm Bằng Đặc Điểm Hình Thái
        </h1>
        <p style={{ textAlign: 'center', color: '#6b7280', marginBottom: '2rem' }}>
          Chọn các đặc điểm của cây nấm để hệ thống AI dự đoán độ an toàn.
        </p>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontWeight: 'bold', color: '#374151' }}>Hình dạng mũ nấm (Cap Shape):</label>
            <select name="cap_shape" value={formData.cap_shape} onChange={handleChange} style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option value="bell">Hình chuông (bell)</option>
              <option value="conical">Hình nón (conical)</option>
              <option value="convex">Khum tròn / lồi (convex)</option>
              <option value="flat">Phẳng (flat)</option>
              <option value="knobbed">Có bướu (knobbed)</option>
              <option value="sunken">Lõm xuống (sunken)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontWeight: 'bold', color: '#374151' }}>Bề mặt mũ nấm (Cap Surface):</label>
            <select name="cap_surface" value={formData.cap_surface} onChange={handleChange} style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option value="fibrous">Có sợi (fibrous)</option>
              <option value="grooves">Có rãnh (grooves)</option>
              <option value="scaly">Có vảy (scaly)</option>
              <option value="smooth">Nhẵn mịn (smooth)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontWeight: 'bold', color: '#374151' }}>Màu sắc mũ nấm (Cap Color):</label>
            <select name="cap_color" value={formData.cap_color} onChange={handleChange} style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option value="brown">Nâu (brown)</option>
              <option value="buff">Vàng kem (buff)</option>
              <option value="cinnamon">Quế (cinnamon)</option>
              <option value="gray">Xám (gray)</option>
              <option value="green">Xanh lá (green)</option>
              <option value="pink">Hồng (pink)</option>
              <option value="purple">Tím (purple)</option>
              <option value="red">Đỏ (red)</option>
              <option value="white">Trắng (white)</option>
              <option value="yellow">Vàng (yellow)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontWeight: 'bold', color: '#374151' }}>Mùi hương (Odor):</label>
            <select name="odor" value={formData.odor} onChange={handleChange} style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option value="almond">Hạnh nhân (almond)</option>
              <option value="anise">Hồi (anise)</option>
              <option value="creosote">Dầu creosote (creosote)</option>
              <option value="fishy">Mùi cá (fishy)</option>
              <option value="foul">Hôi thối (foul)</option>
              <option value="musty">Mùi mốc (musty)</option>
              <option value="none">Không mùi (none)</option>
              <option value="pungent">Hăng cay (pungent)</option>
              <option value="spicy">Mùi gia vị (spicy)</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontWeight: 'bold', color: '#374151' }}>Môi trường mọc (Habitat):</label>
            <select name="habitat" value={formData.habitat} onChange={handleChange} style={{ padding: '0.5rem', borderRadius: '6px', border: '1px solid #d1d5db' }}>
              <option value="grasses">Bãi cỏ (grasses)</option>
              <option value="leaves">Lá mục (leaves)</option>
              <option value="meadows">Đồng cỏ (meadows)</option>
              <option value="paths">Đường mòn (paths)</option>
              <option value="urban">Khu đô thị (urban)</option>
              <option value="waste">Bãi rác / đất hoang (waste)</option>
              <option value="woods">Rừng cây (woods)</option>
            </select>
          </div>

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
              fontSize: '1rem'
            }}
          >
            {loading ? 'Đang phân tích đặc điểm...' : 'Dự Đoán Độc Tính Nấm'}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: '#fee2e2', color: '#b91c1c', borderRadius: '8px' }}>
            {error}
          </div>
        )}

        {result && (
          <div style={{ marginTop: '1.5rem', padding: '1.5rem', backgroundColor: '#ecfdf5', borderRadius: '8px', border: '1px solid #10b981' }}>
            <h3 style={{ color: '#065f46', marginTop: 0 }}>Kết quả dự đoán:</h3>
            <p><strong>Khả năng:</strong> {result.label || result.prediction || 'Không xác định'}</p>
            <p><strong>Độ tin cậy:</strong> {result.confidence ? `${(result.confidence * 100).toFixed(2)}%` : 'N/A'}</p>
            {result.description && <p><strong>Chi tiết:</strong> {result.description}</p>}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;