import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit'
import type { RootState } from '@/store'
import { login as loginApi, getMe, logout as logoutApi } from '@/api/auth'
import { setTokens, clearTokens, getTokens } from '@/utils/request'

export interface UserProfile {
  id: number
  username: string
  nickname: string
  email: string
  phone: string | null
  avatar: string | null
  is_superuser: boolean
  is_staff: boolean
  roles: string[]
  dept: { id: number; name: string } | null
  last_login_time: string | null
  created_at: string
  updated_at: string
}

export interface MenuNode {
  id: number
  name: string
  path: string
  component: string
  icon: string
  menu_type: string
  visible: boolean
  permission_id: number | null
  children: MenuNode[]
}

interface AuthState {
  token: string
  refresh: string
  user: UserProfile | null
  permissions: string[]
  menus: MenuNode[]
  loaded: boolean
}

const initTokens = getTokens()

const initialState: AuthState = {
  token: initTokens?.access || '',
  refresh: initTokens?.refresh || '',
  user: null,
  permissions: [],
  menus: [],
  loaded: false,
}

// 登录：返回 {access, refresh, user}
export const loginThunk = createAsyncThunk(
  'auth/login',
  async (payload: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const data = await loginApi(payload)
      setTokens({ access: data.access, refresh: data.refresh })
      return data
    } catch (err) {
      return rejectWithValue(err)
    }
  }
)

// 拉取个人信息（含 permissions / menus）
export const loadProfile = createAsyncThunk('auth/me', async () => {
  const data = await getMe()
  return data
})

// 登出
export const logoutThunk = createAsyncThunk('auth/logout', async (_, { getState }) => {
  const { refresh } = (getState() as RootState).auth
  try {
    if (refresh) await logoutApi(refresh)
  } catch {
    // 忽略登出接口错误
  }
  clearTokens()
})

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    resetAuth: (state) => {
      state.token = ''
      state.refresh = ''
      state.user = null
      state.permissions = []
      state.menus = []
      state.loaded = false
    },
    setMenus: (state, action: PayloadAction<MenuNode[]>) => {
      state.menus = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginThunk.fulfilled, (state, action) => {
        state.token = action.payload.access
        state.refresh = action.payload.refresh
        state.user = action.payload.user
      })
      .addCase(loadProfile.fulfilled, (state, action) => {
        state.user = action.payload
        state.permissions = action.payload.permissions || []
        state.menus = action.payload.menus || []
        state.loaded = true
      })
      .addCase(logoutThunk.fulfilled, (state) => {
        state.token = ''
        state.refresh = ''
        state.user = null
        state.permissions = []
        state.menus = []
        state.loaded = false
      })
  },
})

export const { resetAuth, setMenus } = authSlice.actions
export default authSlice.reducer
