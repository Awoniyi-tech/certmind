import { create } from 'zustand'

export const useStore = create((set, get) => ({
  selectedCert: 'hcip-datacom',
  setCert: (cert) => set({ selectedCert: cert }),

  certifications: [
    { id: 'hcip-datacom',  vendor: 'Huawei', name: 'HCIP Datacom Core' },
    { id: 'hcip-security', vendor: 'Huawei', name: 'HCIP Security' },
    { id: 'hcia-datacom',  vendor: 'Huawei', name: 'HCIA Datacom' },
    { id: 'ccna',          vendor: 'Cisco',  name: 'CCNA' },
    { id: 'ccnp-ent',      vendor: 'Cisco',  name: 'CCNP Enterprise' },
    { id: 'aws-saa',       vendor: 'AWS',    name: 'AWS Solutions Architect' },
  ],

  activeExam: null,
  setActiveExam: (exam) => set({ activeExam: exam }),
  clearActiveExam: () => set({ activeExam: null }),
}))
