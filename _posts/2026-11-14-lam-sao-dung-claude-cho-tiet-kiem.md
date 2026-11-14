---
title: "Dùng Claude Code sao cho tiết kiệm: token đi đâu sau mỗi lần nhấn Enter"
slug: "lam-sao-dung-claude-cho-tiet-kiem"
date: 2026-11-14 09:00:00 +0700
categories: [ai]
lang: vi
---

Ba giờ chiều. Con bug đang sửa dở, bạn gõ thêm một câu, và Claude Code đáp lại bằng một dòng lạnh tanh: bạn đã dùng hết hạn mức.

Khoan đã. Từ sáng tới giờ bạn gõ được mấy chục câu, câu nào cũng chỉ một hai dòng. Hạn mức đi đâu hết? Ai trả tiền theo API key thì gặp câu hỏi này muộn hơn một chút: cuối tháng, lúc mở hóa đơn ra.

Thủ phạm không phải là những gì bạn gõ. Mỗi lần bạn nhấn Enter, Claude Code lặng lẽ gửi đi một lượng chữ nhiều gấp hàng nghìn lần câu bạn gõ, và gửi không chỉ một lần. Bạn trả tiền cho phần chìm đó.

Vậy thì lật phần chìm lên xem. Trong đó có gì? Vì sao nó cứ phình ra? Và thứ gì đang âm thầm gánh hóa đơn giúp bạn? Trả lời xong ba câu này, mẹo tiết kiệm nào bạn cũng tự nghĩ ra được.

{% include toc.html %}

## Người đồng nghiệp không có trí nhớ

Thử hình dung bạn có một đồng nghiệp cực giỏi, chỉ mắc một tật lạ: nói xong câu nào là quên sạch câu đó. Muốn nhờ tiếp, bạn phải đưa lại cả tập hồ sơ. Nội quy công ty, ghi chú về dự án, mọi thứ hai bên đã trao đổi từ sáng, rồi mới tới câu hỏi mới. Lần nào cũng thế.

Model đứng sau Claude Code y hệt như vậy. Câu bạn vừa hỏi, nó không nhớ. File nó vừa đọc một phút trước, cũng không. Người ôm tập hồ sơ chạy tới chạy lui là Claude Code, và mỗi lần gửi, nó xếp vào đó:

- phần hướng dẫn hệ thống và danh sách công cụ,
- file CLAUDE.md và ghi nhớ của dự án,
- toàn bộ cuộc hội thoại từ đầu, kể cả nội dung những file đã đọc và kết quả những lệnh đã chạy,
- cuối cùng mới là câu bạn vừa gõ.

{% include cc-vi-ho-so.html %}

Chưa hết đâu. Một lần nhấn Enter không phải là một lần gửi.

Bạn gõ "sửa giúp lỗi đăng nhập". Claude đáp: cho tôi xem file này. Claude Code đọc file, kẹp nội dung vào hồ sơ, gửi lại cả tập. Claude bảo: chạy test thử xem. Kẹp kết quả vào, gửi lại cả tập. Cứ thế cho tới khi Claude có câu trả lời. Một yêu cầu cần mười lần dùng công cụ là khoảng mười một lần gửi, lần sau dày hơn lần trước.

{% include cc-vi-nhieu-lan-gui.html %}

Tất cả những thứ trong hồ sơ được đếm bằng **token**. Một token là một mẩu chữ, trung bình bằng khoảng ba phần tư một từ tiếng Anh. Gửi lên bao nhiêu token, Claude viết ra bao nhiêu token, bạn trả tiền bấy nhiêu.

Giờ thì rõ hạn mức đi đâu rồi. Câu bạn gõ chỉ là tờ cuối cùng, mỏng nhất. Tiền nằm ở cả tập hồ sơ đi kèm nó, nhân với số lần gửi.

## Đọc lại thì rẻ hơn đọc mới

Tới đây chắc bạn đang nghĩ: lần nào cũng gửi lại tất cả, vậy một buổi làm việc dài phải đắt khủng khiếp chứ?

Đúng ra là thế. May mà có **prompt cache**.

Ý tưởng rất gọn. Tập hồ sơ lần này giống hệt lần trước, chỉ thêm vài trang ở cuối? Vậy máy chủ khỏi xử lý lại từ đầu. Phần cũ dùng lại kết quả đã có và tính giá rất rẻ. Chỉ phần mới phải xử lý kỹ.

| Loại | Giá so với bình thường |
|---|---|
| Gửi lên bình thường | 1 lần |
| Ghi vào cache | 1,25 lần (đắt hơn một chút, trả một lần) |
| Đọc lại từ cache | 0,1 lần, các model mới còn rẻ hơn |

Rẻ tới mức nào? Tôi đã cộng số liệu của một phiên làm việc thật, phiên viết ra [bài tiếng Anh về cách Claude Code hoạt động]({% post_url 2026-10-26-how-claude-code-works-sessions-cache-tokens %}), gồm 1.593 lần model trả lời. Trong số token gửi lên, 96,7% là đọc lại từ cache. Phần gửi lên nhờ vậy rẻ hơn khoảng 86% so với khi không có cache.

{% include cc-vi-cache.html %}

Tin vui là phần lớn chuyện tiết kiệm đã có người làm sẵn cho bạn. Việc của bạn chỉ là đừng phá nó. Mà cache thì có đúng hai cách để mất.

**Để nguội.** Cache chỉ sống một lúc kể từ lần dùng cuối: 5 phút nếu bạn dùng API key, 1 giờ cho cuộc hội thoại chính nếu bạn dùng gói thuê bao. Quá giờ, lần gửi kế tiếp phải ghi lại cả tập hồ sơ với giá ghi. Dùng API key thì đi pha ly cà phê là đủ nguội.

**Làm vỡ.** Cache chỉ dùng lại được khi phần đầu hồ sơ còn nguyên. Mấy việc sau đây đụng vào phần đầu đó, và lần gửi tiếp theo phải dựng lại tất cả:

- đổi model giữa chừng bằng `/model`,
- đổi mức effort hoặc bật tắt fast mode,
- thêm hoặc gỡ một MCP server,
- chạy `/compact`,
- nâng cấp Claude Code.

{% include cc-vi-cache-mat.html %}

Không việc nào trong danh sách này là cấm kỵ cả. Cứ làm, nhưng làm ở đầu phiên hoặc lúc chuyển việc. Đừng làm giữa một phiên đang dài.

## Ba điều nhiều người hiểu nhầm

### "Hôm qua làm rồi, hôm nay mở lại sẽ rẻ hơn"

Tiếc là không. Phiên làm việc được lưu thành một file trên máy bạn. Giữ nó không tốn đồng nào, nhưng nó cũng chẳng tiết kiệm cho bạn đồng nào. Mở lại phiên cũ, Claude Code gửi lại nguyên cuộc hội thoại. Cache còn ấm thì rẻ. Sáng hôm sau mới mở thì bạn trả tiền ghi lại tất cả.

Muốn mang hiểu biết của hôm qua sang hôm nay với giá rẻ, hãy trông vào CLAUDE.md và phần ghi nhớ của dự án. Chúng ngắn. Cuộc hội thoại thì không.

### "Cài thêm MCP server là tiết kiệm token"

Còn tùy server. Công cụ tiết kiệm được khi câu trả lời của nó thay cho việc đọc cả đống file. Hỏi "hàm này được gọi ở đâu" và nhận về một danh sách ngắn, thế là rẻ hơn hẳn so với tìm rồi đọc năm file.

Nhưng công cụ nào cũng có giá. Phần mô tả công cụ tốn token, kết quả nó trả về thì nằm lại trong hồ sơ. Server gọn, trả lời ngắn: có lợi. Server vài chục công cụ, mỗi lần trả về vài nghìn token: ngược lại. Cái nào không dùng, tắt đi bằng `/mcp`.

### "Context tới một triệu token, cứ dùng thoải mái"

Một triệu token là sức chứa của tập hồ sơ, không phải thứ bạn trả tiền. Bạn trả cho những gì đang nằm trong đó, mỗi lần gửi. Và nó đầy nhanh hơn bạn tưởng: chạy cả bộ test một lần là có thể đã thêm vài chục nghìn token.

## Tiền đi đâu nhiều nhất

**File lớn và kết quả lệnh.** Bạn cần xem một hàm, Claude đọc cả file. Một lệnh in ra cả nghìn dòng log. Đã vào hồ sơ là ở lại, và đi theo mọi lần gửi về sau.

**Một phiên ôm nhiều việc.** Sáng sửa lỗi thanh toán, trưa viết tài liệu, chiều đổi giao diện, tất cả trong một cuộc hội thoại. Tới việc buổi chiều, mỗi lần gửi vẫn cõng theo file và kết quả của hai việc trước.

{% include cc-vi-clear.html %}

**Ảnh chụp màn hình.** Một tấm tốn từ khoảng 1.500 token, ngang một trang chữ. Hai mươi tấm trong một buổi debug là hơn 30.000 token cộng vào *mỗi* lần gửi sau đó. Log hay thông báo lỗi vốn là chữ, vậy cứ dán chữ.

**Phần Claude viết ra.** Token viết ra đắt gấp vài lần token gửi lên, vì model phải viết từng token một. Phần Claude "suy nghĩ" trước khi trả lời cũng tính vào đây. Trong phiên tôi đo, suy nghĩ chiếm khoảng 29% lượng viết ra. Đổi tên một biến thì đâu cần nghĩ nhiều thế: hạ xuống bằng `/effort`.

**Subagent.** Mỗi subagent là một cuộc hội thoại riêng với tập hồ sơ riêng. Rất có ích, lát nữa sẽ nói, nhưng không miễn phí.

Còn một chuyện riêng của người viết tiếng Việt. Chữ có dấu hay bị tách thành nhiều token hơn, nên cùng một ý, tiếng Việt có thể tốn gấp 1,5 đến 2 lần tiếng Anh. Câu bạn gõ hằng ngày thì khỏi lo. Đáng để ý là những thứ có mặt ở mọi phiên, như CLAUDE.md: viết thật ngắn, và nếu cả nhóm đọc được thì viết bằng tiếng Anh.

## Bảy thói quen

**1. Xong một việc thì `/clear`.** Thói quen đáng tiền nhất. Cuộc hội thoại cũ biến mất, chỉ còn phần cố định (hướng dẫn hệ thống, công cụ, CLAUDE.md), vốn nhỏ và thường vẫn còn trong cache.

**2. Còn làm tiếp việc đó thì `/compact`, kèm một câu nói rõ cần giữ gì.** Ví dụ: `/compact tập trung vào phần refactor thanh toán`. Claude tóm tắt cuộc hội thoại, giữ phần bạn cần, bỏ phần còn lại. Compact làm vỡ cache, nên hãy dùng ở chỗ nghỉ tự nhiên, đừng dùng lúc đang điều tra dở. Sang việc khác hẳn thì `/clear`, vì bản tóm tắt vẫn cõng theo việc cũ.

**3. Hỏi ngang thì `/btw`.** Đang làm mà muốn hỏi nhanh "cờ này nghĩa là gì"? Hỏi bằng `/btw`. Bạn vẫn có câu trả lời, còn hồ sơ không dày thêm tờ nào.

**4. Chọn model, mức effort và MCP server ngay từ đầu phiên.** Đổi giữa chừng là vỡ cache. Có một loạt việc vặt? Mở hẳn một phiên riêng với model rẻ hơn.

**5. Chỉ đúng chỗ ngay từ câu đầu tiên.** "Sửa lỗi đăng nhập" bắt Claude phải đi dò, và file nào nó mở ra để dò cũng nằm lại trong hồ sơ. "Hàm `validateToken` trong `auth/session.ts` trả về sai khi token hết hạn" thì đi thẳng tới nơi.

**6. Việc ồn ào thì giao cho subagent.** Chạy test, lục log, rà cả codebase: toàn những việc sinh ra cả núi chữ trong khi bạn chỉ cần kết luận. Subagent làm trong hồ sơ riêng của nó rồi gửi về đúng bản tóm tắt. Việc đơn giản thì cho nó chạy bằng Haiku.

**7. Giữ CLAUDE.md ngắn.** File này có mặt trong mọi lần gửi của mọi phiên. Tài liệu khuyên giữ dưới 200 dòng. Với từng dòng, hỏi một câu thôi: bỏ dòng này thì Claude có làm sai không? Không thì xóa. Hướng dẫn thỉnh thoảng mới cần thì chuyển sang skill, vì skill chỉ được nạp khi dùng tới.

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

Nói thật, lúc đang đuổi theo một con bug thì chẳng ai nhớ nổi mẹo tiết kiệm token. Cách chắc ăn hơn: xếp ngày làm việc sao cho việc tiết kiệm tự nó xảy ra.

{% include cc-vi-mot-ngay.html %}

**Sáng: mười phút xếp việc.** Chia việc trong ngày làm ba nhóm. Việc lớn: cần hiểu sâu, mất cả giờ. Việc vặt: vài phút, không dính tới việc khác. Và một khoảng trống, chừng 20 đến 30% thời gian, để dành cho việc phát sinh. Gom các việc lớn có liên quan vào cùng một khối, chọn luôn model cho từng khối.

**Mỗi khối là một phiên, một chủ đề.** Làm liền một mạch. Muốn nghỉ thì nghỉ giữa hai khối, vì nghỉ giữa khối là để cache nguội. Hết khối thì `/clear`.

**Việc gấp chen ngang: đừng gõ vào phiên đang mở.** Làm vậy là kéo cả đống file không liên quan vào tập hồ sơ bạn đã dày công xây. Chỉ là một câu hỏi? `/btw`. Là một việc hẳn hoi? Mở terminal thứ hai, chạy phiên mới ở đó. Xong thì đóng lại. Phiên chính vẫn y nguyên như lúc bạn rời đi.

**Cuối ngày: làm việc vặt một lượt.** Trong ngày, việc vặt nào tới thì ghi vào danh sách, khoan làm. Cuối ngày mở một phiên với model rẻ, làm lần lượt, xong mỗi việc lại `/clear`. Việc nào tuần nào cũng gặp thì biến thành skill, lần sau gõ một dòng là xong.

**Trước khi về: năm phút.** Bảo Claude ghi nhớ điều đáng nhớ của hôm nay. Hôm nay phải nhắc Claude hai lần về cùng một lỗi? Thêm một dòng vào CLAUDE.md. Và đừng để dành một phiên dài cho sáng mai mở tiếp. Sáng mai cache đã nguội, cả cuộc hội thoại sẽ được gửi lại với giá ghi. Mở phiên mới cho nhẹ.

## Đừng đoán, hãy xem số

Bạn không cần tin lời tôi. Claude Code có sẵn đồ nghề để bạn tự kiểm tra:

- `/usage` cho biết phiên này tốn bao nhiêu, chia theo gửi lên, viết ra, đọc cache và ghi cache. Tỉ lệ đọc từ cache thấp? Có thứ gì đó đang liên tục làm vỡ cache.
- `/context` cho biết cái gì đang nằm trong hồ sơ và chiếm bao nhiêu chỗ: CLAUDE.md, phần ghi nhớ, công cụ MCP, các file đã đọc.
- Status line có thể hiện số token đọc và ghi cache ngay trong lúc làm. Vừa bấm một thao tác mà số ghi cache nhảy vọt, bạn biết ngay thói quen nào đang tốn tiền.

## Tóm lại

Dùng Claude tiết kiệm không có nghĩa là hỏi ít đi. Chỉ cần hai việc: giữ cho tập hồ sơ gọn, và đừng phá cache. Mọi mẹo trong bài đều quy về đó. `/clear` và subagent giữ hồ sơ gọn. Chọn model từ đầu và làm liền mạch giữ cho cache còn nguyên.

Chỉ nhớ được một điều thôi? Nhớ `/clear`.
