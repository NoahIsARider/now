# babel

巴别塔。读过的书，用哥特体印成一份密目。

## Temperament and Imagery

Tower of Babel. 砖，泥，低语。密到喘不过气的小字排满整个页，像印刷错误的中世纪抄本。UnifrakturMaguntia 给标题和 masthead mark，其余正文用 Courier Prime 小字压住黑活字的喧宾夺主。

## Visual Strategy

单栏窄幅 720px（同 MAYDAY / shkb 骨架）。字号比 MAYDAY 和 shkb 再小 2-3px，行高更紧。UnifrakturMaguntia 只给 masthead mark (`BABEL`) 和每条书的标题本身——作者、年份、评分、筛选按钮全 Courier Prime 400 小字，避免黑活字全糊。

## Color Scheme (cult core: bone white + blackletter)

| token        | value     | note                              |
|-------------|-----------|-----------------------------------|
| --bg        | `#faf9f6` | warm bone white, paper            |
| --text      | `#1a1a1a` | near black body                   |
| --mark      | `#1a1a1a` | black mark (BABEL + hover)        |
| --link      | `#3a3a3a` | link grey, one step down          |
| --visited   | `#6b6b6b` | visited grey                      |
| --inputbg   | `#f2f0ec` | search wash, slightly deeper      |
| --border    | `#dcd8d3` | paper edge divider                |
| --dim       | `#999`    | secondary label                   |
| --star      | `#1a1a1a` | star color matches body           |

## Typography

| role         | family             | weight | size | note                                    |
|-------------|--------------------|--------|------|-----------------------------------------|
| mast mark   | UnifrakturMaguntia | 400    | 32px | `BABEL`，letter-spacing .12em，烫金    |
| item title  | UnifrakturMaguntia | 400    | 16px | 书标题，走 --link                        |
| author/yr   | Courier Prime      | 400    | 12px | meta                                    |
| stars       | Courier Prime      | 700    | 12px | `★★★☆☆` 右侧                            |
| label/stat  | Courier Prime      | 400    | 11px | 筛选、stats                              |

## Layout

- 单栏 720px，序号 3.4ch
- 书标题链接 Goodreads `https://www.goodreads.com/book/show/<BookId>`
- 右侧 star 评分（zero → 无星）
- meta：author · year
- 筛选：5/4/3 星 OR + 全文搜索（标题/作者）
- `/` 聚焦搜索框，Esc 清空
- 空结果文案 "No book answers to that..."

## Taboos

- 不准卡片、圆角、封面、渐变、发光
- 不准正文全 UnifrakturMaguntia（12px 以下不可读）
- 不准 CJK（全部经 translations.py 转英）
- 不准数字评分数字显示，统一 ★☆

## Execution

- 目录 slug 英文 `babel`，零 CJK
- 字体自托管 woff2
- 71 条 CJK 标题经 translations.py 译成英文进站，0 条被拒
- 构建同 MAYDAY/shkb 同构，根 build.py 串 babel
- favicon：深底烫金 B（UnifrakturMaguntia）
