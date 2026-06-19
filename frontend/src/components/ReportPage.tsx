import React, { useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';

export interface Telemetry {
  device_id: string;
  window_start: string;
  avg_heart_rate: string;
}

const ReportPage: React.FC = () => {
  const { keycloak, initialized } = useKeycloak();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<Telemetry[]>([]);

  const downloadReport = async () => {
    if (!keycloak?.token) {
      setError('Not authenticated');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/reports`, {
        headers: {
          'Authorization': `Bearer ${keycloak.token}`
        }
      });

      const result = await response.json();
      setData(result);

      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (!initialized) {
    return <div>Loading...</div>;
  }

  if (!keycloak.authenticated) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
        <button
          onClick={() => keycloak.login()}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Login
        </button>
      </div>
    );
  }

  const userEmail = keycloak.tokenParsed?.email;
  const preferred_username = keycloak.tokenParsed?.preferred_username;

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <div className="p-8 bg-white rounded-lg shadow-md">
        <h1 className="text-2xl font-bold mb-6">Usage Reports</h1>
        
        <h3 className="text-l font-bold mb-6">Logged in as: {preferred_username}</h3>
        <h3 className="text-l font-bold mb-6">Email: {userEmail}</h3>
        
        <button
          onClick={downloadReport}
          disabled={loading}
          className={`px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 ${
            loading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {loading ? 'Generating Report...' : 'Download Report'}
        </button>

        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
          <thead>
            <tr style={{ backgroundColor: '#f2f2f2', textAlign: 'left' }}>
              <th style={cellStyle}>Device ID</th>
              <th style={cellStyle}>Date</th>
              <th style={cellStyle}>Average heart rate</th>
            </tr>
          </thead>
          <tbody>
            {data.map((telemetry) => (
              <tr key={telemetry.device_id} style={{ borderBottom: '1px solid #ddd' }}>
                <td style={cellStyle}><strong>{telemetry.device_id}</strong></td>
                <td style={cellStyle}><strong>{telemetry.window_start}</strong></td>
                <td style={cellStyle}>{telemetry.avg_heart_rate}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

const cellStyle: React.CSSProperties = {
  padding: '12px',
  borderBottom: '1px solid #ddd'
};

export default ReportPage;

