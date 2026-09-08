# 构建中文 EPUB

使用与中文 PDF 相同的 Markdown 源码构建 EPUB 3 电子书。

安装 [Pandoc](https://pandoc.org/) 和 Poppler（提供 `pdftoppm`）；可选安装 [EPUBCheck](https://www.w3.org/publishing/epubcheck/) 自动验证生成结果。

先生成中文 PDF，构建脚本会将 PDF 首页用作 EPUB 封面：

```bash
(cd book && bash build_pdf.sh)
./build_epub.sh
```

也可使用 `./build_epub.sh zh-CN`；兼容参数 `all` 同样只构建中文版。

输出文件为 `book/深入理解-AI-Agent-李博杰-v2.0.epub`。生成的 EPUB 文件已被 Git 忽略。
