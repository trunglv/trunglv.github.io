---
title: "Dùng Claude Code sao cho tiết kiệm: token đi đâu sau mỗi lần nhấn Enter"
slug: "lam-sao-dung-claude-cho-tiet-kiem"
date: 2026-11-14 09:00:00 +0700
categories: [ai]
lang: vi
---

Ba giờ chiều. Con bug đang sửa dở thì Claude Code hiện thông báo: bạn đã dùng hết hạn mức. Bạn ngồi nhẩm lại. Cả ngày mình gõ được mấy chục câu, câu nào cũng ngắn. Vậy hạn mức đi đâu hết?

Ai trả tiền theo API key thì gặp phiên bản khác của cùng câu chuyện: cuối tháng mở hóa đơn ra và không hiểu mình đã làm gì mà tốn đến thế.

Câu trả lời gói trong một câu: bạn gõ rất ít, nhưng Claude Code gửi đi rất nhiều. Bài này kể chuyện gì xảy ra sau mỗi lần bạn nhấn Enter. Hiểu được chuyện đó thì các mẹo tiết kiệm không cần học thuộc nữa, vì bạn tự suy ra được.

Bài này không dịch lại [bài gốc tiếng Anh]({% post_url 2026-10-26-how-claude-code-works-sessions-cache-tokens %}) mà kể lại theo một mạch khác. Bảng giá đầy đủ và số liệu chi tiết nằm ở bài gốc, viết theo tài liệu chính thức của Anthropic tính đến tháng 10/2026. Claude Code thay đổi nhanh, nên trước khi dựa vào một con số cụ thể, bạn nên kiểm tra lại tài liệu.

{% include toc.html %}

## Người đồng nghiệp không có trí nhớ

Hãy hình dung bạn làm việc với một đồng nghiệp rất giỏi nhưng mắc một chứng lạ: nói xong câu nào là quên sạch câu đó. Muốn nhờ tiếp, bạn phải đưa lại cả tập hồ sơ: nội quy công ty, ghi chú về dự án, toàn bộ những gì hai bên đã trao đổi từ sáng, rồi mới tới câu hỏi mới. Lần nào cũng vậy.

Model đứng sau Claude Code đúng là như thế. Nó không nhớ câu bạn vừa hỏi, cũng không nhớ file nó vừa đọc một phút trước. Claude Code là người ôm tập hồ sơ. Mỗi lần gửi đi, nó xếp vào đó:

- phần hướng dẫn hệ thống và danh sách công cụ,
- file CLAUDE.md và ghi nhớ của dự án,
- toàn bộ cuộc hội thoại từ đầu, gồm cả nội dung những file đã đọc và kết quả những lệnh đã chạy,
- cuối cùng mới là câu bạn vừa gõ.

{% include cc-vi-ho-so.html %}

Chưa hết. Một lần bạn nhấn Enter không phải là một lần gửi. Giả sử bạn gõ "sửa giúp lỗi đăng nhập". Claude trả lời: cho tôi xem file này. Claude Code đọc file, kẹp nội dung vào hồ sơ, gửi lại cả tập. Claude bảo: chạy test thử. Lại kẹp kết quả vào, lại gửi cả tập. Cứ thế cho tới khi Claude có câu trả lời cho bạn. Một yêu cầu cần mười lần dùng công cụ là khoảng mười một lần gửi, lần sau dày hơn lần trước.

{% include cc-vi-nhieu-lan-gui.html %}

Mọi thứ trong tập hồ sơ được đếm bằng **token**. Token là một mẩu chữ, trung bình bằng khoảng ba phần tư một từ tiếng Anh. Bạn trả tiền theo số token gửi lên và số token Claude viết ra.

Vậy là rõ hạn mức đi đâu. Câu bạn gõ chỉ là tờ cuối cùng, mỏng nhất. Thứ tốn tiền là cả tập hồ sơ đi kèm nó, nhân với số lần nó được gửi đi.

## Đọc lại thì rẻ hơn đọc mới

Nghe tới đây, bạn có thể thắc mắc: nếu lần nào cũng gửi lại tất cả, một buổi làm việc dài phải đắt khủng khiếp chứ?

Đúng ra là vậy, nếu không có **prompt cache**. Ý tưởng của nó thế này: khi tập hồ sơ gửi lên giống hệt lần trước và chỉ thêm vài trang ở cuối, máy chủ không xử lý lại từ đầu. Nó dùng lại kết quả đã có cho phần cũ, chỉ xử lý kỹ phần mới, và tính tiền phần cũ rất rẻ.

| Loại | Giá so với bình thường |
|---|---|
| Gửi lên bình thường | 1 lần |
| Ghi vào cache | 1,25 lần (đắt hơn một chút, trả một lần) |
| Đọc lại từ cache | 0,1 lần, các model mới còn rẻ hơn |

Tôi đã cộng số liệu của chính phiên làm việc viết ra bài gốc, gồm 1.593 lần model trả lời. Trong số token gửi lên, 96,7% được đọc lại từ cache. Nhờ vậy phần gửi lên rẻ hơn khoảng 86% so với khi không có cache.

{% include cc-vi-cache.html %}

Nói cách khác, phần lớn chuyện tiết kiệm đã được làm sẵn cho bạn. Việc của bạn là đừng phá nó. Cache có hai cách để mất.

**Để nguội.** Cache chỉ sống một thời gian ngắn kể từ lần dùng cuối: 5 phút nếu bạn dùng API key, 1 giờ cho cuộc hội thoại chính nếu bạn dùng gói thuê bao. Quá thời gian đó, lần gửi kế tiếp phải ghi lại cả tập hồ sơ với giá ghi. Dùng API key thì chỉ cần đi pha ly cà phê là đủ nguội.

**Làm vỡ.** Cache chỉ dùng lại được khi phần đầu hồ sơ không đổi. Những việc sau thay đổi phần đầu đó, nên lần gửi tiếp theo phải dựng lại từ đầu:

- đổi model giữa chừng bằng `/model`,
- đổi mức effort hoặc bật tắt fast mode,
- thêm hoặc gỡ một MCP server,
- chạy `/compact`,
- nâng cấp Claude Code.

{% include cc-vi-cache-mat.html %}

Không có việc nào trong danh sách này là cấm kỵ. Chỉ cần làm chúng ở đầu phiên hoặc lúc chuyển việc, đừng làm giữa một phiên đang dài.

## Ba điều nhiều người hiểu nhầm

### "Hôm qua đã làm rồi, hôm nay mở lại sẽ rẻ hơn"

Không. Phiên làm việc được lưu thành một file trên máy bạn. Giữ file đó không tốn gì, nhưng nó cũng không giúp tiết kiệm gì. Khi bạn mở lại phiên cũ, Claude Code gửi lại nguyên cuộc hội thoại. Mở lại trong lúc cache còn ấm thì rẻ. Mở lại vào sáng hôm sau thì bạn trả tiền ghi lại tất cả.

Thứ mang được hiểu biết từ hôm qua sang hôm nay với giá rẻ là CLAUDE.md và phần ghi nhớ của dự án, vì chúng ngắn. Cuộc hội thoại thì không.

### "Cài thêm MCP server là tiết kiệm token"

Tùy server. Một công cụ tiết kiệm khi câu trả lời của nó thay cho việc đọc nhiều file. Hỏi "hàm này được gọi ở đâu" và nhận về một danh sách ngắn thì rẻ hơn nhiều so với tìm rồi đọc năm file.

Nhưng công cụ cũng có giá: phần mô tả công cụ tốn token, và kết quả nó trả về sẽ nằm lại trong hồ sơ. Một server gọn, trả lời ngắn thì có lợi. Một server có vài chục công cụ, mỗi lần trả về vài nghìn token thì ngược lại. Server nào không dùng, hãy tắt đi bằng `/mcp`.

### "Context tới một triệu token, cứ dùng thoải mái"

Một triệu token là sức chứa tối đa của tập hồ sơ. Bạn không trả tiền cho sức chứa, bạn trả cho những gì đang nằm trong đó, mỗi lần gửi. Và nó đầy nhanh hơn bạn nghĩ: kết quả của một lần chạy cả bộ test có thể đã là vài chục nghìn token.

## Tiền đi đâu nhiều nhất

**File lớn và kết quả lệnh.** Bạn chỉ cần xem một hàm nhưng Claude đọc cả file. Một lệnh in ra cả nghìn dòng log. Những thứ này vào hồ sơ rồi là ở lại, và đi theo mọi lần gửi về sau.

**Một phiên ôm nhiều việc.** Sáng sửa lỗi thanh toán, trưa viết tài liệu, chiều đổi giao diện, tất cả trong một cuộc hội thoại. Tới việc buổi chiều, mỗi lần gửi vẫn chở theo file và kết quả của hai việc trước.

{% include cc-vi-clear.html %}

**Ảnh chụp màn hình.** Một ảnh tốn từ khoảng 1.500 token, ngang một trang chữ. Hai mươi ảnh trong một buổi debug là hơn 30.000 token cộng vào *mỗi* lần gửi sau đó. Nếu thứ bạn muốn đưa là chữ, như log hay thông báo lỗi, hãy dán chữ.

**Phần Claude viết ra.** Token viết ra đắt gấp vài lần token gửi lên, vì model phải viết từng token một. Phần Claude "suy nghĩ" trước khi trả lời cũng tính vào đây. Trong phiên tôi đo, suy nghĩ chiếm khoảng 29% lượng viết ra. Với việc đơn giản như đổi tên biến, hãy hạ mức suy nghĩ bằng `/effort`.

**Subagent.** Mỗi subagent là một cuộc hội thoại riêng với tập hồ sơ riêng. Nó có ích, như phần dưới sẽ nói, nhưng không miễn phí.

Còn một chuyện riêng của người viết tiếng Việt. Chữ có dấu thường bị tách thành nhiều token hơn, nên cùng một ý, tiếng Việt có thể tốn gấp 1,5 đến 2 lần tiếng Anh. Với câu bạn gõ hằng ngày thì không đáng bận tâm. Thứ đáng để ý là những gì được gửi đi ở mọi phiên, như CLAUDE.md: hãy viết thật ngắn, và nếu cả nhóm đọc được thì viết bằng tiếng Anh.

## Bảy thói quen

**1. Xong một việc thì `/clear`.** Đây là thói quen đáng tiền nhất. Lệnh này bỏ hết cuộc hội thoại cũ. Thứ còn lại là phần cố định (hướng dẫn hệ thống, công cụ, CLAUDE.md), vốn nhỏ và thường vẫn còn trong cache.

**2. Còn làm tiếp việc đó thì `/compact`, kèm một câu nói rõ cần giữ gì.** Ví dụ: `/compact tập trung vào phần refactor thanh toán`. Claude tóm tắt cuộc hội thoại, giữ phần bạn cần và bỏ phần còn lại. Vì compact làm vỡ cache, hãy dùng ở chỗ nghỉ tự nhiên chứ đừng dùng lúc đang điều tra dở. Chuyển sang việc khác hẳn thì dùng `/clear`, vì bản tóm tắt vẫn mang theo việc cũ.

**3. Hỏi ngang thì dùng `/btw`.** Đang làm mà muốn hỏi nhanh "cờ này nghĩa là gì", hãy hỏi bằng `/btw`. Bạn vẫn nhận được câu trả lời, nhưng nó không được kẹp vào hồ sơ.

**4. Chọn model, mức effort và MCP server ngay từ đầu phiên.** Đổi giữa chừng là vỡ cache. Nếu có một loạt việc vặt, hãy mở hẳn một phiên riêng với model rẻ hơn.

**5. Chỉ đúng chỗ ngay từ câu đầu tiên.** "Sửa lỗi đăng nhập" buộc Claude phải đi dò, và mỗi file nó mở ra để dò đều nằm lại trong hồ sơ. "Hàm `validateToken` trong `auth/session.ts` trả về sai khi token hết hạn" thì đi thẳng tới nơi.

**6. Việc ồn ào thì giao cho subagent.** Chạy test, lục log, rà cả codebase là những việc sinh ra rất nhiều chữ mà bạn chỉ cần kết luận. Subagent làm trong hồ sơ riêng của nó rồi chỉ gửi về bản tóm tắt. Việc đơn giản thì cho subagent chạy bằng Haiku.

**7. Giữ CLAUDE.md ngắn.** File này có mặt trong mọi lần gửi của mọi phiên. Tài liệu khuyên giữ dưới 200 dòng. Với từng dòng, hãy hỏi: bỏ dòng này thì Claude có làm sai không? Nếu không thì xóa. Hướng dẫn chỉ thỉnh thoảng mới cần thì chuyển sang skill, vì skill chỉ được nạp khi dùng tới.

Bản rút gọn để dán cạnh màn hình:

| Tình huống | Làm gì |
|---|---|
| Xong việc, chuyển sang việc không liên quan | `/clear` |
| Vẫn việc đó nhưng hội thoại đã dài | `/compact` kèm trọng tâm |
| Muốn hỏi nhanh một câu ngoài lề | `/btw` |
| Có việc gấp chen ngang | Mở terminal thứ hai, chạy phiên mới |
| Cần chạy test, lục log | Giao cho subagent |
| Một loạt việc vặt | Phiên riêng với model rẻ |
| Sắp nghỉ lâu | Kết thúc việc đang làm, lần sau mở phiên mới |

## Một ngày làm việc tiết kiệm

Lúc đang đuổi theo một con bug, không ai nhớ nổi mẹo tiết kiệm token. Cách chắc ăn hơn là xếp ngày làm việc sao cho việc tiết kiệm tự nó xảy ra.

{% include cc-vi-mot-ngay.html %}

**Sáng: mười phút xếp việc.** Chia việc trong ngày làm ba nhóm. Việc lớn là việc cần hiểu sâu, mất cả giờ. Việc vặt là việc vài phút, không dính tới việc khác. Phần thứ ba là khoảng trống, chừng 20 đến 30% thời gian, dành cho việc phát sinh. Gom các việc lớn có liên quan vào cùng một khối và chọn luôn model cho từng khối.

**Mỗi khối là một phiên, một chủ đề.** Làm liền một mạch. Muốn nghỉ thì nghỉ giữa hai khối, vì nghỉ giữa khối là để cache nguội. Hết khối thì `/clear`.

**Việc gấp chen ngang: đừng gõ vào phiên đang mở.** Làm vậy là kéo cả đống file không liên quan vào tập hồ sơ bạn đã dày công xây. Nếu chỉ là một câu hỏi, dùng `/btw`. Nếu là một việc, mở terminal thứ hai và chạy phiên mới ở đó. Xong thì đóng lại. Phiên chính vẫn y nguyên như lúc bạn rời đi.

**Cuối ngày: làm việc vặt một lượt.** Trong ngày, việc vặt nào tới thì ghi vào danh sách chứ đừng làm ngay. Cuối ngày mở một phiên với model rẻ, làm lần lượt, mỗi việc xong lại `/clear`. Việc nào tuần nào cũng gặp thì biến thành skill, lần sau chỉ cần gõ một dòng.

**Trước khi về: năm phút.** Bảo Claude ghi nhớ điều đáng nhớ của hôm nay. Nếu bạn đã phải nhắc Claude hai lần về cùng một lỗi, thêm một dòng vào CLAUDE.md. Và đừng để dành một phiên dài cho sáng mai mở tiếp. Sáng mai cache đã nguội, cả cuộc hội thoại sẽ được gửi lại với giá ghi. Hãy mở phiên mới.

## Đừng đoán, hãy xem số

Bạn không cần tin lời bài này. Claude Code có sẵn công cụ để tự kiểm tra:

- `/usage` cho biết phiên này tốn bao nhiêu, chia theo gửi lên, viết ra, đọc cache và ghi cache. Nếu tỉ lệ đọc từ cache thấp, có thứ gì đó đang liên tục làm vỡ cache.
- `/context` cho biết cái gì đang nằm trong hồ sơ và chiếm bao nhiêu chỗ: CLAUDE.md, phần ghi nhớ, công cụ MCP, các file đã đọc.
- Status line có thể hiện số token đọc và ghi cache ngay trong lúc làm. Vừa làm một thao tác mà số ghi cache nhảy vọt, bạn biết ngay thói quen nào đang tốn tiền.

## Tóm lại

Dùng Claude tiết kiệm không có nghĩa là hỏi ít đi. Nó có nghĩa là giữ cho tập hồ sơ gọn, và đừng phá cache. Mọi mẹo trong bài đều quy về hai việc đó: `/clear` và subagent giữ hồ sơ gọn, còn chọn model từ đầu và làm liền mạch thì giữ cache.

Nếu chỉ nhớ được một điều, hãy nhớ `/clear`.
