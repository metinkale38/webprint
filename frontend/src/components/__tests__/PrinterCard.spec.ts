import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { Printer } from '@/types'

import PrinterCard from '../PrinterCard.vue'

const printer: Printer = {
  id: 1,
  name: 'Testdrucker',
  slug: 'testdrucker',
  device_uri: 'ipp://192.0.2.10/ipp/print',
  protocol: 'ipp',
  model: 'Testmodell',
  location: 'Erdgeschoss',
  driver_mode: 'everywhere',
  auto_discovered: false,
  enabled: true,
  status: 'idle',
  capabilities: {},
}

describe('PrinterCard', () => {
  it('zeigt Name, Standort und deutschen Status', () => {
    const wrapper = mount(PrinterCard, { props: { printer } })

    expect(wrapper.text()).toContain('Testdrucker')
    expect(wrapper.text()).toContain('Erdgeschoss')
    expect(wrapper.text()).toContain('Bereit')
  })

  it('emittiert select beim Klick', async () => {
    const wrapper = mount(PrinterCard, { props: { printer } })

    await wrapper.trigger('click')

    expect(wrapper.emitted('select')).toHaveLength(1)
  })
})
