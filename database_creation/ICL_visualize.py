import networkx as nx
import matplotlib.pyplot as plt

def main():
    # 有向グラフの作成
    G = nx.DiGraph()

    # ノードの追加
    G.add_node("Graph Elements\n(ノード/エッジ)")
    G.add_node("Logical Deletion\n(論理削除: deleted_at)",font_color='red')
    G.add_node("Deletion Record\n(削除記録保存)")
    G.add_node("Normal Record\n(記録保存)")
    G.add_node("User Actions\n(ユーザー操作)")
    G.add_node("LLM Auto-editing\n(LLM自動編集)")
    G.add_node("Chat Data Sync\n(チャットデータ同期)")
    G.add_node("Learning Data Update\n(学習データ更新)")
    G.add_node("LLM Context Learning\n(LLM編集上下文学習)")

    # エッジの追加（各プロセスの流れを定義）
    G.add_edge("Logical Deletion\n(論理削除: deleted_at)", "Deletion Record\n(削除記録保存)")
    # ユーザー操作とLLM自動編集は、削除記録とともにチャットデータの同期へフィードバック
    G.add_edge("Deletion Record\n(削除記録保存)", "Graph Elements\n(ノード/エッジ)")
    G.add_edge( "Normal Record\n(記録保存)","Graph Elements\n(ノード/エッジ)")
    G.add_edge("Graph Elements\n(ノード/エッジ)", "Chat Data Sync\n(チャットデータ同期)")
    G.add_edge("User Actions\n(ユーザー操作)", "Chat Data Sync\n(チャットデータ同期)")
    G.add_edge("LLM Auto-editing\n(LLM自動編集)", "Chat Data Sync\n(チャットデータ同期)")
    G.add_edge("Chat Data Sync\n(チャットデータ同期)", "Learning Data Update\n(学習データ更新)")
    G.add_edge("Learning Data Update\n(学習データ更新)", "LLM Context Learning\n(LLM編集上下文学習)")

    # レイアウトの設定（spring layoutを使用）
    pos = nx.spring_layout(G)

    # グラフ描画
    plt.figure(figsize=(12, 8))
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=4000, alpha=0.9)
    nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, edge_color='gray')
    # 绘制其他节点标签 (黑色)
    other_nodes = [node for node in G.nodes() if node != "Logical Deletion\n(論理削除: deleted_at)"]
    nx.draw_networkx_labels(G, pos, labels={node: node for node in other_nodes}, font_size=10, font_family='SimSun', font_color='black')

    # 绘制 "Logical Deletion" 节点标签 (红色)
    red_nodes = ["Logical Deletion\n(論理削除: deleted_at)"]
    nx.draw_networkx_labels(G, pos, labels={node: node for node in red_nodes}, font_size=10, font_family='SimSun', font_color='red')

    plt.title("Logical Deletion & Data Sync Flow for LLM Context Learning", fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
