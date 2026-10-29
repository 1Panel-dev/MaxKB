"""Small, deterministic model artifacts; no model hub or pretrained weights required."""

from pathlib import Path


def build_local_sentence_transformer(directory):
    import torch
    from sentence_transformers import SentenceTransformer
    from sentence_transformers.sentence_transformer.modules import Pooling, Transformer
    from transformers import BertConfig, BertModel, BertTokenizer

    directory = Path(directory)
    backbone_path = directory / "backbone"
    model_path = directory / "sentence-model"
    vocabulary = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "hello", "world", "test", "文", "档", "查", "询"]
    tokenizer = BertTokenizer(vocab={word: i for i, word in enumerate(vocabulary)})
    config = BertConfig(
        vocab_size=len(vocabulary),
        hidden_size=12,
        intermediate_size=24,
        num_hidden_layers=1,
        num_attention_heads=3,
        max_position_embeddings=128,
        hidden_dropout_prob=0,
        attention_probs_dropout_prob=0,
    )
    with torch.random.fork_rng():
        torch.manual_seed(20261029)
        BertModel(config).save_pretrained(backbone_path)
    tokenizer.save_pretrained(backbone_path)
    transformer = Transformer(str(backbone_path), max_seq_length=32, model_kwargs={"local_files_only": True})
    sentence_model = SentenceTransformer(modules=[transformer, Pooling(12, pooling_mode="mean")], device="cpu")
    sentence_model.save_pretrained(str(model_path))
    return str(model_path)
