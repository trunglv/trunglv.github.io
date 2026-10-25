---
title: "Plug-in và mã nguồn mở của Anthropic: cập nhật tuần 43 của năm 2026"
date: 2026-10-25 09:10:00 +0700
categories: [ai]
lang: vi
---

Tuần này nhiều repo plug-in và công cụ mã nguồn mở của Anthropic được cập nhật trên GitHub. Dưới đây là những repo đáng chú ý nhất với người xây dựng hệ thống, dựa trên README của từng repo. Ngày ghi là ngày commit gần nhất, không phải ngày phát hành ban đầu.

## Plug-in cho công việc tri thức trên Claude Cowork

Repo [knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) chứa các plug-in biến Claude thành chuyên gia cho từng vai trò công việc. Anthropic đã mã nguồn mở 11 plug-in, bao gồm năng suất, bán hàng, chăm sóc khách hàng, quản lý sản phẩm, marketing, pháp lý, tài chính, dữ liệu, tìm kiếm nội bộ, nghiên cứu sinh học và quản lý plug-in. Mỗi plug-in gói kỹ năng, connector, lệnh slash và sub-agent. Bạn có thể cài trong Cowork, hoặc trong Claude Code qua marketplace.

## Thư mục plug-in chính thức cho Claude Code

Repo [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) là thư mục plug-in được Anthropic chọn lọc cho Claude Code. Bạn cài bằng lệnh `/plugin install {tên-plugin}@claude-plugins-official`, hoặc duyệt trong `/plugin > Discover`. Anthropic cho biết plug-in của bên thứ ba phải qua kiểm duyệt chất lượng và bảo mật trước khi được liệt kê, và nhắc người dùng kiểm tra kỹ trước khi cài.

## Marketplace cộng đồng

Repo [claude-plugins-community](https://github.com/anthropics/claude-plugins-community) là bản sao chỉ đọc của marketplace plug-in cộng đồng cho Cowork và Claude Code. Nhà phát triển nộp plug-in qua một form riêng, không qua repo này.

## Claude for Legal

Repo [claude-for-legal](https://github.com/anthropics/claude-for-legal) là bộ plug-in cho công việc pháp lý, gồm mảng thương mại nội bộ, quyền riêng tư, lao động và tranh tụng. Repo có các agent được đặt tên theo công việc, như Vendor Agreement Reviewer và NDA Triager. README nhấn mạnh mọi kết quả chỉ là bản nháp để luật sư rà soát, không phải tư vấn pháp lý.

## Sandbox runtime

Repo [sandbox-runtime](https://github.com/anthropics/sandbox-runtime), tên lệnh là `srt`, đang ở giai đoạn xem trước nghiên cứu (beta). Công cụ này giới hạn quyền truy cập file và mạng của tiến trình ở cấp hệ điều hành, không cần container. Nó có thể bao các agent, MCP server cục bộ và lệnh shell. Cài bằng `npm install -g @anthropic-ai/sandbox-runtime`. README cho biết API và định dạng cấu hình có thể thay đổi.

## Điều này có ý nghĩa gì với bạn

Nếu bạn xây dựng quy trình agent, các repo plug-in là tài liệu tham khảo thực tế về connector, kỹ năng và sub-agent. Sandbox runtime quan trọng nếu bạn chạy agent trên máy có dữ liệu thật.
