const DATASET = 'https://aikosh.indiaai.gov.in/home/datasets/details/all_colleges_as_per_aishe_dashboard_3.html'

/** Required by the Government Open Data License - India. Please don't remove it. */
export function CollegeAttribution() {
  return (
    <p className="mt-6 text-xs text-muted">
      College directory: Department of Higher Education, Ministry of Education,{' '}
      <a href={DATASET} target="_blank" rel="noopener noreferrer">All Colleges as per AISHE Dashboard</a>, AIKosh.
      Published under the Government Open Data License - India. PathMithra is not endorsed by the data provider.
    </p>
  )
}
