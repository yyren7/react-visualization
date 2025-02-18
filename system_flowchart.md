# 系统流程图

```mermaid
graph LR
    A[用户输入] --> B{System Prompt组装}
    B --> C[Prompt截断处理]
    C --> D{截断决策者}
    D --> E[大模型调用_Claude_Deepseek_API]
    E --> F{多轮交互}
    F -- 工具调用 --> G[工具执行结果]
    F -- 需要工具 --> H[解析响应]
    H -- 直接回复 --> I[直接回答]
    I --> J[更新progress]
    J --> K[更新activeContext]
    K --> L[Memory Bank系统]
    L --> M[输出处理结果]
    M --> N[用户输出]
    N --> O[上下文更新触发]
    O --> P[更新触发条件]

    subgraph Prompt 准备阶段
        B
        C
        D
    end

    subgraph 大模型处理阶段
        E
    end

    subgraph 多轮交互与工具调用阶段
        F
        G
        H
        I
        J
        K
    end

    subgraph Memory Bank 系统
        L
        L1[productContext.md]
        L2[历史记录]
        L --> L1
        L --> L2
    end

    subgraph 用户输出与上下文更新
        M
        N
        O
        P
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#ccf,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#aaf,stroke:#333,stroke-width:2px
    style F fill:#afa,stroke:#333,stroke-width:2px
    style G fill:#afa,stroke:#333,stroke-width:2px
    style H fill:#afa,stroke:#333,stroke-width:2px
    style I fill:#afa,stroke:#333,stroke-width:2px
    style J fill:#afa,stroke:#333,stroke-width:2px
    style K fill:#afa,stroke:#333,stroke-width:2px
    style L fill:#eee,stroke:#333,stroke-width:2px
    style M fill:#eee,stroke:#333,stroke-width:2px
    style N fill:#eee,stroke:#333,stroke-width:2px
    style O fill:#eee,stroke:#333,stroke-width:2px
    style P fill:#eee,stroke:#333,stroke-width:2px

    subgraph 截断决策者
        D1[API提供者]
        D2[Client应用]
        D3[模型特性]
        D --> D1
        D --> D2
        D --> D3
    end

    subgraph System Prompt组装
        B1[prompt模板]
        B2[.clinerules]
        B --> B1
        B --> B2
    end

    subgraph 更新触发条件:
        P1[用户新消息]
        P2[工具调用结果]
        P3[大模型响应]
        P4[会话状态变化]
        P --> P1
        P --> P2
        P --> P3
        P --> P4
    end

    subgraph 注释
        Q[知乎 @橘子科技]
        R[橘子科技出品 必然是精品]
        Q --> R
    end

    classDef highlight fill:#f9f,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P highlight
