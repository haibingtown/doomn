export const BASE_URL = "http://localhost:8000"

export type FetchOptions = RequestInit & {
    auth?: boolean    
};

export const DEFAULT_HEADERS: Record<string, string> = {
    'credentials': 'include',
    'Content-Type': 'application/json',
};

// 封装 fetch 请求
export const fetchAPI = async (url: string, options: FetchOptions = { auth:false }): Promise<any> => {
    // 默认需要本地鉴权
    options = {
        auth: true,
        ...options
    }

    try {
        const response = await fetch(`${BASE_URL}${url}`, {
            ...DEFAULT_HEADERS,
            ...options,
        });

        // 如果未授权或禁止访问，跳转到登录页面
        if (response.status === 401 || response.status === 403) {
            // redirectToLogin();
            return Promise.reject(new Error('Unauthorized: Redirecting to login'));
        }

        // 解析 JSON 响应
        if (response.ok) {
            return response.json();
        }

        // 处理 400 状态的特定错误
        if (response.status === 400) {
            const errorData = await response.json(); // 等待解析 JSON 数据
            return Promise.reject(new Error(errorData.message));
        }

        // 其他错误状态处理
        const errorText = await response.text();
        return Promise.reject(new Error(errorText));
    } catch (error) {
        console.error('Fetch Error:', error);
        return Promise.reject(error);
    }
};

export type FetchParams = {
    url: string;
    data?: any; // 用于 POST/PUT 请求的数据
    params?: Record<string, any>; // 用于 GET/DELETE 请求的查询参数
    options?: RequestInit; // 其他配置项
  };
  
// 格式化查询参数为 URL
export const formatQueryParams = (params?: Record<string, any>): string => {
    if (!params) return '';
    const query = new URLSearchParams(params).toString();
    return query ? `?${query}` : '';
};

// GET 请求
export const fetchGet = async <T = any>({ url, params, options }: FetchParams): Promise<T> => {
    const query = formatQueryParams(params);
    return fetchAPI(`${url}${query}`, {
        method: 'GET',
        ...options,
    });
};

// POST 请求
export const fetchPost = async <T = any>({ url, data, options }: FetchParams): Promise<T> => {
    return fetchAPI(url, {
        method: 'POST',
        body: JSON.stringify(data),
        ...options,
    });
};

// PUT 请求
export const fetchPut = async <T = any>({ url, data, options }: FetchParams): Promise<T> => {
    return fetchAPI(url, {
        method: 'PUT',
        body: JSON.stringify(data),
        ...options,
    });
};

// DELETE 请求
export const fetchDel = async <T = any>({ url, params, options }: FetchParams): Promise<T> => {
    const query = formatQueryParams(params);
    return fetchAPI(`${url}${query}`, {
        method: 'DELETE',
        ...options,
    });
};
export const loadDesign = async (uuid: string) => {
    const data = await fetchGet({url: `design/${uuid}`});
    return data.json;
}

export const uploadImage = async (imageFile: File) => {
  const formData = new FormData();
  formData.append('image', imageFile);
  return await fetchAPI('/upload_image', {
    method: 'POST',
    body: formData,
  });
};

export const translateImage = async (params: {
  from_lan: string;
  to_lan: string; 
  image_url: string;
}) => {
  return await fetchAPI('/pic_trans', {
    method: 'POST',
    body: JSON.stringify(params),
    headers: {
      'Content-Type': 'application/json'
    }
  });
};

export const saveDesign = async (uuid: string, formData: FormData, options?: RequestInit) => {
    return await fetchAPI(`design/${uuid}`, {
        method: 'POST',
        body: formData,
        ...options
    });
}
