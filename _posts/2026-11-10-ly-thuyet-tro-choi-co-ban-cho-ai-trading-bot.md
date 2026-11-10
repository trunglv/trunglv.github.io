---
title: "Lý thuyết trò chơi cơ bản cho trading và vai trò của harness cho AI bot"
slug: "ly-thuyet-tro-choi-co-ban-cho-ai-trading-bot"
date: 2026-11-10 09:00:00 +0700
categories: [finance, ai]
lang: vi
image: /assets/images/posts/ly-thuyet-tro-choi-co-ban-cho-ai-trading-bot-banner.png
---

![Lý thuyết trò chơi cơ bản cho trading và vai trò của harness cho AI bot]({{ "/assets/images/posts/ly-thuyet-tro-choi-co-ban-cho-ai-trading-bot-banner.png" | relative_url }})

> **Lưu ý rủi ro trước khi đọc.** Dùng AI để trading không có nghĩa là chắc thắng. Model ngôn ngữ lớn không biết trước giá, không có thông tin gì mà thị trường chưa có, và hàng trăm nghìn bot khác cũng đang dùng model tương tự với cùng dữ liệu. Một bot chạy bằng AI vẫn có thể thua lỗ đều đặn, thậm chí mất sạch vốn trong vài phút nếu lỗi và không có nút dừng. Bài này không chỉ cách kiếm lời bằng bot. Nó giải thích vì sao thị trường là một trò chơi với đối thủ, và harness, tức lớp giới hạn và kiểm tra bao quanh model, là thứ giữ cho bot không tự giết mình. Chỉ giao dịch bằng số tiền bạn chấp nhận mất.

Ngày càng nhiều nhà đầu tư cá nhân để một con bot chạy bằng AI đặt lệnh thay mình. Cách làm phổ biến là lấy một model ngôn ngữ lớn, cho nó đọc giá, tin tức, chỉ báo, rồi hỏi "mua hay bán?". Phần lớn công sức đổ vào việc chọn model và viết prompt. Phần ít được để ý hơn, nhưng quyết định bot sống hay chết, là **harness**: lớp vỏ bao quanh model, gồm các giới hạn, kiểm tra và nút dừng, quyết định một đề xuất của model có được biến thành lệnh thật hay không.

Để viết harness tốt, cần hiểu một điều mà nhiều người mới bỏ qua: thị trường không phải một bài toán có đáp án đúng, mà là một **trò chơi**. Kết quả của bạn phụ thuộc vào lựa chọn của người khác, và những người khác cũng đang đoán bạn. Nhánh toán học nghiên cứu chuyện này gọi là lý thuyết trò chơi. Bài này đi qua các ý cơ bản nhất, bằng ví dụ đời thường, rồi dịch từng ý thành một quy tắc cụ thể cho harness. Theo góc nhìn riêng:

- Phần lớn thua lỗ của bot không đến từ việc model đoán sai hướng giá, mà từ việc bot chơi một chiến lược dễ đoán, trong một trò chơi mà đối thủ đang đọc nó.
- Khi nhiều người cùng dùng một loại model với cùng loại dữ liệu, các bot sẽ ra quyết định giống nhau. Tín hiệu mà ai cũng thấy thì không còn ăn được nữa.
- Lý thuyết trò chơi không giúp đoán giá. Nó giúp bạn đặt đúng câu hỏi khi thiết kế harness: "ai đang ở bên kia lệnh của tôi, và họ biết gì mà tôi không biết?"

{% include toc.html %}

## Toàn cảnh trong một sơ đồ

{% include ly-thuyet-tro-choi-flow.html %}

## Trò chơi là gì?

Trong lý thuyết trò chơi, một "trò chơi" chỉ cần ba thứ:

- **Người chơi**: những ai tham gia ra quyết định. Trong oẳn tù tì là hai người. Trên thị trường là hàng triệu người và bot.
- **Chiến lược**: các lựa chọn mỗi người có. Búa, kéo, bao. Mua, bán, đứng ngoài.
- **Kết quả**: mỗi người được hay mất gì, tùy theo tổ hợp lựa chọn của tất cả.

Điểm khác biệt với một bài toán bình thường nằm ở chữ "tùy theo tổ hợp lựa chọn của tất cả". Nếu bạn gieo xúc xắc, kết quả không quan tâm bạn nghĩ gì. Nếu bạn chơi oẳn tù tì, kết quả phụ thuộc vào người đối diện, và người đó cũng đang đoán bạn. Thị trường giống oẳn tù tì hơn giống xúc xắc.

Một hình ảnh quen thuộc từ nhà kinh tế [Keynes](https://en.wikipedia.org/wiki/Keynesian_beauty_contest): một cuộc thi trên báo, người đọc chọn ra 6 gương mặt đẹp nhất trong 100 bức ảnh, ai chọn trúng nhóm được nhiều người chọn nhất sẽ thắng. Người chơi khôn không chọn ảnh mình thấy đẹp, mà chọn ảnh họ nghĩ người khác sẽ chọn. Người khôn hơn nữa chọn ảnh họ nghĩ người khác nghĩ người khác sẽ chọn. Mua cổ phiếu hay coin ngắn hạn cũng vậy: bạn không cần biết tài sản đó "thật sự" đáng giá bao nhiêu, bạn cần đoán xem đám đông sẽ nghĩ nó đáng giá bao nhiêu.

## Tổng bằng không, tổng dương, tổng âm

Cách phân loại đầu tiên: cộng hết được và mất của mọi người lại thì ra bao nhiêu?

- **Tổng bằng không**: người này được đúng bằng người kia mất. Đánh bài ăn tiền giữa bạn bè là ví dụ. Tổng tiền trên bàn không đổi, chỉ chuyển từ túi này sang túi khác.
- **Tổng dương**: cả hai cùng được. Bạn bán xe cũ cho người cần xe. Bạn thích tiền hơn xe, họ thích xe hơn tiền, cả hai đều vui.
- **Tổng âm**: cộng lại thì mọi người mất. Đánh bài ở sòng có thu phí: tổng tiền trên bàn giảm dần theo từng ván, phần giảm đó đi vào nhà cái.

Thị trường tài chính ở đâu? Nếu nhìn dài hạn, đầu tư cổ phiếu là trò chơi tổng dương, vì doanh nghiệp tạo ra lợi nhuận và chia cho cổ đông. Nhưng nếu nhìn rất ngắn hạn, kiểu mua sáng bán chiều, giá trị doanh nghiệp gần như không thay đổi trong vài giờ. Lúc này bạn lời bao nhiêu thì người khớp lệnh với bạn lỗ bấy nhiêu. Thêm phí giao dịch, chênh lệch giá mua bán và trượt giá, trò chơi trở thành tổng âm: giống sòng bài có thu phí.

Hệ quả đầu tiên cho bot: **một bot giao dịch nhiều trong ngày đang chơi trò chơi tổng âm**. Nó phải thắng đối thủ đủ nhiều để bù phí rồi mới có lời. Nếu lợi thế của nó nhỏ hơn chi phí mỗi lệnh, càng giao dịch nhiều càng lỗ đều, dù model đoán hướng đúng hơn sai.

## Thế lưỡng nan của người tù

Đây là trò chơi nổi tiếng nhất, và dễ hiểu nhất. Hai nghi phạm bị bắt, giam riêng. Mỗi người có hai lựa chọn: im lặng hoặc khai người kia. Kết quả như sau, tính theo số năm tù, số nhỏ là tốt hơn:

| | B im lặng | B khai |
|---|---|---|
| **A im lặng** | A: 1 năm, B: 1 năm | A: 10 năm, B: 0 năm |
| **A khai** | A: 0 năm, B: 10 năm | A: 5 năm, B: 5 năm |

Nhìn từ phía A: nếu B im lặng, A khai thì được thả ngay, tốt hơn 1 năm. Nếu B khai, A khai thì 5 năm, tốt hơn 10 năm. Vậy dù B làm gì, A khai đều tốt hơn. B suy nghĩ y hệt. Kết quả: cả hai khai, mỗi người 5 năm, trong khi nếu cả hai im lặng thì chỉ 1 năm.

Bài học: **mỗi người chọn điều tốt nhất cho mình, và kết quả chung lại tệ cho tất cả.** Không ai ngu. Chính cấu trúc trò chơi đẩy họ tới đó.

Thị trường đầy những tình huống như vậy. Khi có tin xấu, mỗi người nghĩ "nếu người khác bán mà mình không bán, mình lỗ nặng; vậy tốt nhất bán trước". Ai cũng nghĩ thế, giá sập, ai cũng lỗ hơn so với việc cùng ngồi yên. Rút tiền ồ ạt khỏi ngân hàng cũng là bài toán này. Với bot, tình huống quen thuộc là nhiều bot cùng nhận một tín hiệu bán, cùng bán, giá xuống nhanh hơn dự kiến, kích hoạt lệnh cắt lỗ của bot khác, thêm một đợt bán nữa.

## Cân bằng Nash: khi không ai muốn đổi ý một mình

Cân bằng Nash, đặt theo tên nhà toán học [John Nash](https://en.wikipedia.org/wiki/Nash_equilibrium), là trạng thái mà **không ai có lợi nếu đổi chiến lược một mình**, khi những người khác giữ nguyên.

Ví dụ dễ nhất: lái xe bên phải. Nếu mọi người lái bên phải, một mình bạn chuyển sang bên trái thì chỉ có hại. Lái bên trái cũng là một cân bằng, như ở Anh hay Nhật. Cân bằng không có nghĩa là tốt nhất, chỉ có nghĩa là ổn định. Trong thế lưỡng nan của người tù, "cả hai khai" là cân bằng Nash, dù "cả hai im lặng" tốt hơn cho cả hai.

Cách áp dụng vào bot cần một chút suy nghĩ. Giả sử có một tín hiệu đơn giản: "mỗi khi giá vượt đường trung bình 50 ngày thì mua". Nếu rất ít người dùng, tín hiệu có thể có lời. Nhưng khi tín hiệu lan rộng, nhiều người mua ngay khi giá chạm ngưỡng, giá bị đẩy lên trước, ai vào sau mua giá đắt. Dần dần, lợi nhuận của tín hiệu đó giảm về gần không, thậm chí âm sau phí. Trạng thái "không còn ai ăn được từ tín hiệu này" chính là một cân bằng: không ai có lợi nếu bắt đầu dùng nó.

Điều này rất đáng lo ở thời điểm hiện tại. Hàng trăm nghìn bot đang chạy trên vài model ngôn ngữ giống nhau, đọc cùng nguồn tin, dùng cùng loại chỉ báo. Khi hỏi "mua hay bán?", chúng có xu hướng trả lời giống nhau. Nói cách khác, **lợi thế của bạn không nằm ở việc có AI, vì ai cũng có. Nó nằm ở việc bạn làm khác số đông, hoặc ít nhất là biết mình đang đứng trong đám đông để không bị giẫm đạp.**

## Chiến lược hỗn hợp: đoán được là thua

Trong oẳn tù tì, nếu bạn luôn ra búa, đối thủ sẽ nhận ra và luôn ra bao. Cách chơi tốt nhất là ra ngẫu nhiên, mỗi thứ một phần ba. Lý thuyết trò chơi gọi đây là [chiến lược hỗn hợp](https://en.wikipedia.org/wiki/Strategy_(game_theory)): thay vì một lựa chọn cố định, bạn chọn ngẫu nhiên theo xác suất. Không phải vì ngẫu nhiên là thông minh, mà vì **không thể bị đọc bài**.

Thị trường là nơi "bị đọc bài" rất đắt. Vài kiểu quen thuộc:

- **Lệnh cắt lỗ đặt ở số tròn.** Rất nhiều người đặt cắt lỗ ở các mốc như 100.000 đồng hay 60.000 USD. Những người chơi lớn biết điều đó. Họ chỉ cần đẩy giá chạm mốc, hàng loạt lệnh cắt lỗ kích hoạt, họ mua lại rẻ hơn. Dân trong nghề gọi là săn stop.
- **Lệnh lớn đẩy ra một lần.** Một lệnh mua lớn xuất hiện trên sổ lệnh là một lời báo trước. Người khác mua trước bạn, rồi bán lại cho bạn giá cao hơn.
- **Bot đặt lệnh đúng một nhịp.** Ví dụ bot luôn kiểm tra và đặt lệnh vào giây thứ 0 mỗi phút, hoặc luôn mua đúng 0,1 BTC mỗi lần. Một bot khác chỉ cần vài ngày để nhận ra quy luật.

Bài học cho harness: **thêm ngẫu nhiên có chủ đích vào cách thực thi.** Chia lệnh lớn thành nhiều lệnh nhỏ với kích thước lệch nhau, thời gian gửi lệch nhau. Không đặt cắt lỗ ở số tròn. Không lặp một nhịp cố định. Lưu ý là phần ngẫu nhiên nằm ở cách thực thi, không nằm ở quyết định mua hay bán. Quyết định vẫn cần lý do.

## Trò chơi lặp lại: uy tín và trả đũa

Thế lưỡng nan của người tù đổi hẳn tính chất khi chơi nhiều lần với cùng một người. Nếu hôm nay bạn phản bội, ngày mai người kia sẽ phản bội lại. Vì vậy hợp tác trở nên có lợi. Nhà khoa học chính trị [Robert Axelrod](https://en.wikipedia.org/wiki/The_Evolution_of_Cooperation) từng tổ chức giải đấu cho các chương trình máy tính chơi trò này lặp đi lặp lại. Chiến lược thắng là một chiến lược rất đơn giản tên là "ăn miếng trả miếng": lượt đầu hợp tác, các lượt sau làm đúng như đối thủ vừa làm với mình.

Ba bài học từ trò chơi lặp lại cho bot:

- **Sàn giao dịch nhớ bạn.** Một bot gửi và hủy lệnh liên tục sẽ bị sàn giới hạn tốc độ, thậm chí khóa tài khoản. Harness cần đếm số lệnh gửi và hủy mỗi phút, và dừng trước khi chạm giới hạn của sàn.
- **Đối thủ nhớ bạn.** Nếu bot của bạn phản ứng theo một kiểu nhất định mỗi khi giá giật mạnh, bot khác sẽ học được điều đó sau vài lần.
- **Bạn cũng nên nhớ đối thủ.** Nếu một mức giá nào đó liên tục bị "săn stop", harness nên ghi nhận và tránh đặt lệnh ở đó.

## Thông tin không đầy đủ: vì sao người kia chịu bán cho bạn?

Mọi trò chơi ở trên giả định mọi người biết luật và biết kết quả. Thực tế, điều quan trọng nhất trên thị trường là **mỗi người biết một ít khác nhau**. Từ đây có hai khái niệm rất đáng nhớ.

**Lời nguyền của người thắng.** Trong một cuộc đấu giá, người thắng là người trả cao nhất. Nhưng nếu ai cũng ước lượng giá trị món đồ một cách hợp lý, người trả cao nhất chính là người ước lượng lạc quan nhất, tức là người sai nhiều nhất. Người thắng đấu giá thường trả quá tay. Điều này gọi là [lời nguyền của người thắng](https://en.wikipedia.org/wiki/Winner%27s_curse). Khi bot của bạn là người duy nhất chịu mua ở một mức giá, đó có thể là vì bạn thấy điều người khác không thấy, hoặc vì bạn sai.

**Lựa chọn ngược.** Bạn bán bảo hiểm sức khỏe với một giá cho mọi người. Ai mua nhiều nhất? Người biết mình hay ốm. Người bán bảo hiểm lỗ vì những người mua lại là những người có thông tin bất lợi cho mình. Hiện tượng này gọi là [lựa chọn ngược](https://en.wikipedia.org/wiki/Adverse_selection). Trên thị trường, khi bot của bạn treo một lệnh mua và có người khớp ngay, hãy tự hỏi: vì sao họ chịu bán cho mình ở giá này? Thường thì không sao. Nhưng nếu lệnh của bạn luôn được khớp ngay trước khi giá đi ngược, nghĩa là người bên kia biết nhiều hơn bạn, và bạn đang là bên mua bảo hiểm cho họ.

Đây có lẽ là bài học quan trọng nhất cho harness: **sau mỗi lần khớp lệnh, đo xem giá đi về đâu trong vài giây, vài phút tiếp theo.** Nếu giá thường xuyên đi ngược lại ngay sau khi khớp, bot đang bị lựa chọn ngược, và vấn đề không nằm ở model mà ở cách bot đặt lệnh.

## Dịch tất cả thành harness

Giờ gom lại. Giả sử bạn có một model, có thể là một model ngôn ngữ lớn hoặc một model thống kê, đưa ra đề xuất "mua X, kích thước Y". Harness đứng giữa đề xuất đó và sàn giao dịch, và nên làm những việc sau:

| Ý trong lý thuyết trò chơi | Câu hỏi harness tự hỏi | Việc harness làm |
|---|---|---|
| Tổng âm sau phí | Lợi nhuận kỳ vọng có lớn hơn phí và trượt giá không? | Tính chi phí trước mỗi lệnh. Chặn lệnh không đủ biên lợi nhuận. Theo dõi tổng phí theo ngày |
| Thế lưỡng nan, bán tháo dây chuyền | Nếu lệnh này kích hoạt phản ứng của người khác thì sao? | Giới hạn vị thế theo mức thanh khoản. Không cắt lỗ bằng lệnh thị trường khi sổ lệnh mỏng |
| Cân bằng Nash, tín hiệu bị dùng nhiều | Có bao nhiêu người đang thấy đúng điều model thấy? | Đo mức đồng thuận với dòng tiền thị trường. Giảm kích thước khi đi cùng đám đông quá rõ |
| Chiến lược hỗn hợp | Bot có đang lặp lại một quy luật không? | Ngẫu nhiên hóa kích thước và thời điểm gửi lệnh. Không dùng số tròn |
| Trò chơi lặp lại | Sàn và đối thủ đã học được gì về bot? | Giới hạn tần suất gửi và hủy lệnh. Ghi nhật ký các mức giá hay bị săn |
| Lựa chọn ngược | Vì sao người kia chịu khớp lệnh với tôi? | Đo giá sau khi khớp. Nếu xấu liên tục, chuyển sang lệnh giới hạn hoặc tạm dừng |
| Mọi trò chơi đều có thể sai | Điều gì xảy ra nếu model hoặc dữ liệu hỏng? | Giới hạn lỗ trong ngày. Nút dừng toàn bộ. Người thật nhận cảnh báo |

Nguyên tắc chung: **model đề xuất, harness quyết định.** Model có thể thông minh, nhưng nó không biết mình đang ở trong trò chơi với ai. Harness là nơi bạn đưa hiểu biết đó vào.

## Hai bài học từ lịch sử

**Flash crash ngày 6/5/2010.** Chỉ số Dow Jones giảm khoảng 1.000 điểm trong vài phút rồi hồi lại. Theo [báo cáo của hai cơ quan quản lý Mỹ](https://www.sec.gov/news/studies/2010/marketevents-report.pdf), một quỹ dùng thuật toán bán 75.000 hợp đồng tương lai với quy tắc chỉ nhìn khối lượng, không nhìn giá và thời gian. Các bot giao dịch tần suất cao mua vào rồi bán lại cho nhau, gọi là hiệu ứng "chuyền củ khoai nóng", đẩy khối lượng lên, khiến thuật toán kia bán nhanh hơn nữa. Đây là trò chơi lặp lại giữa các bot với nhau, trong đó không bot nào sai một mình, nhưng tổ hợp của chúng tạo ra thảm họa. Cũng là ví dụ cho việc một harness thiếu kiểm tra về giá và thời gian có thể gây ra chuyện gì.

**Knight Capital ngày 1/8/2012.** Một lỗi triển khai phần mềm khiến bot của công ty này gửi hàng triệu lệnh sai trong 45 phút, [lỗ khoảng 440 triệu USD](https://www.sec.gov/litigation/admin/2013/34-70694.pdf) và suýt phá sản. Bot không hề thông minh hay ngu, nó chỉ chạy đúng mã cũ bị kích hoạt nhầm. Vấn đề là không có harness nào nói "số lệnh và mức lỗ này bất thường, dừng lại". Đây là bài học cho dòng cuối của bảng ở trên: giới hạn lỗ và nút dừng không phải thứ thêm vào cho đẹp.

## Điều lý thuyết trò chơi không làm được

Để tránh hiểu lầm, vài giới hạn cần nói rõ:

- **Nó không dự đoán giá.** Nó mô tả cấu trúc tương tác, không nói ngày mai giá lên hay xuống.
- **Nó giả định người chơi hợp lý.** Thị trường thật có người hoảng loạn, người mua theo cảm xúc, và bot bị lỗi. Các mô hình đơn giản không bắt được hết.
- **Nó không thay thế quản trị rủi ro.** Dù hiểu trò chơi đến đâu, bạn vẫn cần giới hạn vị thế, giới hạn lỗ và kế hoạch cho trường hợp xấu nhất.

Giá trị của nó nằm ở chỗ khác: nó cho bạn một cách nghĩ. Mỗi khi bot sắp làm gì, hãy hỏi "ai ở bên kia, họ biết gì, họ nghĩ tôi sẽ làm gì?". Chỉ riêng thói quen đó đã tránh được phần lớn những lỗi khiến bot của nhà đầu tư cá nhân mất tiền.

## Kết luận: lợi thế không nằm ở model, mà ở hiểu trò chơi

Khi ai cũng có AI, AI không còn là lợi thế. Hàng trăm nghìn bot dùng cùng vài model, đọc cùng dữ liệu, sẽ nghĩ giống nhau và cùng kẹt trong các bẫy mà lý thuyết trò chơi đã mô tả từ hơn nửa thế kỷ trước: trò chơi tổng âm sau phí, bán tháo dây chuyền, tín hiệu bị dùng đến cạn, chiến lược dễ đoán, và lựa chọn ngược.

Harness là nơi bạn đưa hiểu biết về trò chơi vào bot. Nó không cần phức tạp. Một harness biết tính phí trước khi vào lệnh, biết ngẫu nhiên hóa cách thực thi, biết đo giá sau mỗi lần khớp, biết đếm lệnh gửi lên sàn và biết dừng khi lỗ chạm ngưỡng, đã đứng trên phần lớn bot ngoài kia. Model có thể thuê, harness thì phải tự hiểu mà viết.

*Bài viết chỉ nhằm cung cấp thông tin và kiến thức cơ bản, không phải khuyến nghị đầu tư. Các ví dụ về bot và harness được đơn giản hóa để dễ hiểu. Giao dịch bằng bot tự động có rủi ro mất vốn, kể cả khi đã có harness.*

## Nguồn tham khảo

- [Game Theory](https://plato.stanford.edu/entries/game-theory/), Stanford Encyclopedia of Philosophy
- [Prisoner's Dilemma](https://plato.stanford.edu/entries/prisoner-dilemma/), Stanford Encyclopedia of Philosophy
- [Nash equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium), Wikipedia
- [Strategy (game theory)](https://en.wikipedia.org/wiki/Strategy_(game_theory)), Wikipedia
- [Keynesian beauty contest](https://en.wikipedia.org/wiki/Keynesian_beauty_contest), Wikipedia
- [The Evolution of Cooperation](https://en.wikipedia.org/wiki/The_Evolution_of_Cooperation), Robert Axelrod, Wikipedia
- [Winner's curse](https://en.wikipedia.org/wiki/Winner%27s_curse), Wikipedia
- [Adverse selection](https://en.wikipedia.org/wiki/Adverse_selection), Wikipedia
- [Findings Regarding the Market Events of May 6, 2010](https://www.sec.gov/news/studies/2010/marketevents-report.pdf), báo cáo chung của CFTC và SEC
- [In the Matter of Knight Capital Americas LLC](https://www.sec.gov/litigation/admin/2013/34-70694.pdf), SEC
