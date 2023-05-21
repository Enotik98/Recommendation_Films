const BASE_URL= 'http://127.0.0.1:5000'
export async function sendRequest(url, method, data){
    let headers = ""
    let accessToken = localStorage.getItem("AccessToken")
    if (accessToken) headers = "Bearer " + accessToken;

    const request = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `${headers}`
        }
    };
    if (data) request.body = JSON.stringify(data)
    const response = await fetch(BASE_URL + url, request);
    if (response.status === 401 && url !=="/login") {
        const refreshToken = localStorage.getItem('RefreshToken');
        const responseTokens = await fetch(BASE_URL + '/refresh-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${refreshToken}`
            }
        });
        if (responseTokens.status !== 401) {
            if (responseTokens.ok) {
                const newTokens = await responseTokens.json();
                localStorage.setItem('AccessToken', newTokens['AccessToken']);
                localStorage.setItem('RefreshToken', newTokens['RefreshToken']);
                return await sendRequest(url, method, data);
            } else {
                return responseTokens;
            }
        } else {
            return responseTokens;
        }
    } else {
        return response;
    }
}