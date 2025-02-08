/*
* https://gitgud.io/ahsk/clewd
* https://github.com/h-a-s-k/clewd
*/

// SET YOUR COOKIE BELOW

module.exports = {
    "Cookie": "CH-prefers-color-scheme=dark; __ssid=957acccb25cf1c3174929b9d532a03f; intercom-device-id-lupk8zyo=fce78148-bc94-4928-93a5-fb155a3435bc; sessionKey=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; lastActiveOrg=7d29d500-4edb-4984-881b-512f15186902; activitySessionId=5e2f238e-6397-41c0-98d5-a34a8914c2dc; __stripe_mid=38d352f2-6f1d-46da-b90e-fa66c6c5a8c9486f2c; __cf_bm=RxDppk._gb00eDc3QI5h1OIV7b2jusxrS0UvxT0DnFY-1738926140-1.0.1.1-8hjpl1FEceTCHQ.Le4BZQ6KfEZYkGmsfwzNTXKEVXIl2glvPCwchkhhNX3pkH.ECpkADbO7XcYlSNVjPFanE8A; cf_clearance=9.XTBRIzYvkBe3RL3Nx16jQQmZ9FVY3e.x_DEmdwuf4-1738926141-1.2.1.1-T_ytuOSSUWPV5ddy1VI9DJOMj5wtzQpE2AhqMjCgIpsgptbjwfrFELvcTbh2HA71DEesWefdjwKJtuWSUiTiooyO5uGv4AZg48DQ3v4QoB98rN0XHnUSo51OJKeq.Z3ADgOOCat124xyn9E86VeO5uFzOkfoQOBycyZMjGtIs_FHR0966suKzPwdpfbcWiADNsGWUptmma9_CqCWCCgj8CGRe5kg6cIrOpNWruQ2Djjr5j5AkBwYx7Hb61aWK81kJ2YMEeI.Fzupr555hxMMh2.12nn0BsDjFcvPArfeccY; intercom-session-lupk8zyo=TFRuTm9aT2hheGJZVlBJbTR6cFZBL3lia1VRVHZreFpTcXBzc3YxeTgwRXdpVUlzMEw5WDd3UGh2eXpSNG10bVdLU2pjTlU2ei9ienplNHBKRU0xWjJtNGFZUkczdkY4QWlXRWlNOHR1K3M9LS1samZ1Ly9vRmJtOFliSGNhL0VXWERRPT0=--c825f9dfc6ce2f74d684e14c25f74dafc3fe1f6f; __stripe_sid=e4c8d7a3-1f68-47ad-a1f6-ca73f46ae85e66c6d8",
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