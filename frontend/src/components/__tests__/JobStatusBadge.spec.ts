import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import JobStatusBadge from '../JobStatusBadge.vue'

describe('JobStatusBadge', () => {
  it('zeigt den deutschen Status für wartende Aufträge', () => {
    const wrapper = mount(JobStatusBadge, { props: { status: 'queued' } })
    expect(wrapper.text()).toContain('Wartet')
  })

  it('zeigt den deutschen Status für fertige Aufträge', () => {
    const wrapper = mount(JobStatusBadge, { props: { status: 'completed' } })
    expect(wrapper.text()).toContain('Fertig')
  })
})
