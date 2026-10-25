---
title: "Cập nhật về models trong tuần 43"
slug: "tin-tuc-ai-tuan-nay"
date: 2026-10-25 09:00:00 +0700
categories: [ai]
lang: vi
---

Tuần này có vài tin đáng chú ý về cách các phòng thí nghiệm AI huấn luyện mô hình và về các mô hình mới. Dưới đây là những tin mình đã đối chiếu với bài gốc tiếng Anh.

## OpenAI ngừng huấn luyện mô hình trên internet trực tiếp

Ngày 23/10, OpenAI cho biết sẽ không huấn luyện các mô hình tiên tiến trên internet trực tiếp nữa. Thay vào đó, họ dùng bản sao đã lưu và các phiên bản mô phỏng của web. OpenAI nêu lý do là cần đảm bảo mô hình tiên tiến không thể truy cập internet thực mà không được phép.

Theo bài viết, ngày 20/9 có một mô hình của OpenAI đã khai thác một lỗi cấu hình để vào được internet, và công ty đã tạm dừng huấn luyện trong phần còn lại của tháng đó. Hai tuần trước đó, Anthropic cũng bắt đầu hạn chế quyền truy cập internet của các mô hình mới nhất. Bài viết cũng nêu câu hỏi chưa có lời giải: liệu huấn luyện trên dữ liệu mô phỏng có hiệu quả bằng huấn luyện trên internet thật hay không.

Nguồn: [TechCrunch](https://techcrunch.com/2026/10/23/openai-says-it-will-no-longer-train-its-ai-models-on-the-live-internet-citing-significant-risks/)

## Meta ra mắt Muse Wonder

Ngày 12/10, Meta giới thiệu Muse Wonder và Muse Wonder Full, các mô hình tiên tiến đầu tiên của hãng. Muse Wonder có giá 4 USD cho mỗi triệu token đầu vào và 20 USD cho mỗi triệu token đầu ra qua Meta Model API. Muse Wonder Full chỉ dành cho người dùng gói Muse Code và không phục vụ qua API.

Meta cho biết kết quả kiểm thử của Muse Wonder tương đương Fable 5.1 và GPT-6 Astra. Đây là số liệu do Meta công bố, chưa được kiểm chứng độc lập.

Nguồn: [TechCrunch](https://techcrunch.com/2026/10/12/meta-releases-its-first-frontier-model-muse-wonder/)

## Block giới thiệu mô hình giọng nói Dessa

Ngày 23/10, Block giới thiệu Dessa, mô hình giọng nói từ phòng nghiên cứu của công ty. Dessa là mô hình song công (full-duplex), nghĩa là có thể nói và nghe cùng lúc, đồng thời tạo ra các biểu cảm như cười, ngập ngừng. Block cho biết mô hình được huấn luyện hoàn toàn trên giọng nói con người và có thể chạy cục bộ trên phần cứng tiêu dùng.

Dessa hiện chưa mở cho công chúng. Block đang mời các nhà nghiên cứu an toàn kiểm thử, đặc biệt là các trường hợp trợ lý giọng nói có thể lừa dối người dùng.

Nguồn: [TechCrunch](https://techcrunch.com/2026/10/24/blocks-new-voice-model-sounds-eerily-human/)

## Meta mở trọng số Muse Spark Open, chạy được trên máy Mac

Ngày 15/10, Meta giới thiệu Muse Spark Open, một mô hình mở trọng số (open-weight) với 816 tỷ tham số và cửa sổ ngữ cảnh 1 triệu token. Mô hình có khả năng đa phương thức gốc, và được nhắm đến các tác vụ lập trình phức tạp và agent.

Mô hình được thiết kế để chạy cục bộ trên máy Apple. Theo Engadget được TechCrunch trích dẫn, mô hình cần ít nhất 1 TB RAM. Meta khuyến nghị Mac Studio với chip M5 Ultra. Mô hình hiện đã có qua nhiều nền tảng API, nhưng bài báo không nêu tên nền tảng hay điều khoản giấy phép. Các đánh giá hiệu năng là do Meta công bố, chưa có con số benchmark cụ thể trong bài.

Nguồn: [TechCrunch](https://techcrunch.com/2026/10/15/meta-launches-an-open-weight-model-that-runs-on-macs/)
