import AgentOffice from '@/components/agent-office/App'
import styles from './page.module.css'

export default function AgentOfficePage() {
  return (
    <main className={styles.page}>
      <AgentOffice fullscreen />
    </main>
  )
}
