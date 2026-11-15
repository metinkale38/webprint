import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import type { PrintOptions } from '@/types'

import OptionsSheet from '../OptionsSheet.vue'

const options: PrintOptions = {
  copies: 1,
  duplex: 'one-sided',
  nup: 1,
  color_mode: 'monochrome',
  page_range: '',
  media: 'A4',
}

describe('OptionsSheet', () => {
  it('zeigt die Druckoptionen und schließt sich', async () => {
    const wrapper = mount(OptionsSheet, {
      props: { modelValue: true, options },
    })

    expect(wrapper.text()).toContain('Druckoptionen')
    expect(wrapper.text()).toContain('Doppelseitig')

    const done = wrapper.findAll('button').find((button) => button.text() === 'Fertig')
    expect(done).toBeDefined()
    await done?.trigger('click')

    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([false])
  })

  it('aktualisiert die Kopienanzahl', async () => {
    const wrapper = mount(OptionsSheet, {
      props: { modelValue: true, options },
    })

    await wrapper.find('input[type="number"]').setValue('3')

    const updates = wrapper.emitted('update:options')
    expect(updates).toBeDefined()
    expect((updates?.at(-1)?.[0] as PrintOptions).copies).toBe(3)
  })
})
