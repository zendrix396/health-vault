/*
* https://gitgud.io/ahsk/clewd
* https://github.com/h-a-s-k/clewd
*/

// SET YOUR COOKIE BELOW

module.exports = {
    "Cookie": "CH-prefers-color-scheme=dark; __ssid=957acccb25cf1c3174929b9d532a03f; intercom-device-id-lupk8zyo=fce78148-bc94-4928-93a5-fb155a3435bc; __stripe_mid=38d352f2-6f1d-46da-b90e-fa66c6c5a8c9486f2c; activitySessionId=2aeb11f2-e5ae-441d-a377-6ab3dda51554; __cf_bm=LWRf759Ea5ZzLUFwU60UezI9KJ7t1k2RbecwHEvewgM-1739039776-1.0.1.1-G_4naXzQ.Tg8uameIcAO6Ajn4qbKi4vTmjdA9J4QiFGyPWWAXEkFbYhddT4ov6FRpWORCpKzuvyCjLlxmi8B9A; cf_clearance=4qhx888fRiLzi6va1tjytzpqfP4Rm6opK58o2QkmZGk-1739039778-1.2.1.1-KYoZd9e0tEz4CzKRv2ys93u6QHYnbQc73w5RIIkM_Sl0AqwQ13OaeEgRvdQAgkDZi_IUtL1711aX.LvtYJhFOh9ni4K5XdsG7.6SnvWvZUBLsa7TexE3yApm1HLWlMOcsGb8p_VQCkytTxmvUC.EA1bFEsbQfsDBqsomuM4x0TIapXHdJV4TG8upRCCDRa7miRF88nl_wgDr.elHkaoyDJjpzxFghOOVl9_g3CgfjwN7_SW5DvR4n3S4kasRIPH_UOG6MdEOS8rFnAUnlUfL.MODtzHo84NpeednUQQCimY; sessionKey=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; lastActiveOrg=866891fb-b943-4b1c-865b-afc7a4111460; intercom-session-lupk8zyo=RkJUdzNZZ2NSQzhQbnJ5VmFjNFY4RjkwR2d5ZmR6V0JPTnpheDlPTnVla3VBT1ppSEFRaUxBRUk4enA4Rm1PQVh6MUFoaUNKaDVDRWNTNkw5V3VTaVZoc0dUMlJFcmF2Ym93Qk45VXhZMFU9LS0rczJKZkdlemJkaWl3Y1JPRXhzV0ZBPT0=--ac88dbaf5a61f1b8131818dedf560edf4840c3c4; __stripe_sid=df1bc001-fd93-4293-9651-6694238c049c30a7e9",
    "Ip": "127.0.0.1",
    "Port": 8444,
    "BufferSize": 8,
    "SystemInterval": 3,
    "PromptExperimentFirst": "",
    "PromptExperimentNext": "",
    "PersonalityFormat": "{{char}}'s personality: {{personality}}",
    "ScenarioFormat": "Dialogue scenario and context: {{scenario}}",
    "Settings": {
        "RenewAlways": true,
        "RetryRegenerate": false,
        "PromptExperiments": true,
        "SystemExperiments": true,
        "PreventImperson": true,
        "AllSamples": false,
        "NoSamples": false,
        "StripAssistant": false,
        "StripHuman": false,
        "PassParams": false,
        "ClearFlags": false,
        "PreserveChats": false,
        "LogMessages": false,
        "Superfetch": true,
        "SendImageDepth": 3
    }
}

/*
 BufferSize
 * How many characters will be buffered before the AI types once
 * lower = less chance of `PreventImperson` working properly

 ---

 SystemInterval
 * How many messages until `SystemExperiments alternates`

 ---

 Other settings
 * https://gitgud.io/ahsk/clewd/#defaults
 * and
 * https://gitgud.io/ahsk/clewd/-/blob/master/CHANGELOG.md
 */